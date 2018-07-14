import json
import uuid

import etcd

from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger

# TODO(darshan) this has to be moved to Definition file

TENDRL_SERVICES = [
    "tendrl-node-agent",
    "etcd",
    "tendrl-api",
    "tendrl-gluster-integration",
    "tendrl-monitoring-integration",
    "glusterd",
]


def sync(sync_ttl=None):
    try:
        tags = []
        # update node agent service details
        logger.log(
            "debug",
            NS.publisher_id,
            {"message": "node_sync, Updating Service data"}
        )
        for service in TENDRL_SERVICES:
            s = NS.tendrl.objects.Service(service=service)
            if s.running:
                service_tag = NS.compiled_definitions.get_parsed_defs()[
                    'namespace.tendrl'
                ]['tags'][service.strip("@*")]
                tags.append(service_tag)

                if service_tag == "tendrl/server":
                    tags.append("tendrl/monitor")
            s.save()

        if "tendrl/monitor" not in tags and \
            NS.tendrl_context.integration_id:
            _cluster = NS.tendrl.objects.Cluster(
                integration_id=NS.tendrl_context.integration_id
            ).load()
            # Try to claim orphan "provisioner_%integration_id" tag
            _tag = "provisioner/%s" % _cluster.integration_id
            _is_new_provisioner = False
            NS.node_context = NS.tendrl.objects.NodeContext().load()
            _cnc = None
            _cnc_is_managed = False
            if NS.tendrl.objects.ClusterNodeContext(
                node_id=NS.node_context.node_id
            ).exists():
                _cnc = NS.tendrl.objects.ClusterNodeContext(
                    node_id=NS.node_context.node_id
                ).load()
                if _cnc.is_managed == "yes":
                    _cnc_is_managed = True
            if _cluster.is_managed in [None, '', 'no']:
                if _tag not in NS.node_context.tags:
                    try:
                        _index_key = "/indexes/tags/%s" % _tag
                        _node_id = json.dumps([NS.node_context.node_id])
                        etcd_utils.write(
                            _index_key, _node_id,
                            prevExist=False
                        )
                        etcd_utils.refresh(_index_key, sync_ttl + 50)
                        tags.append(_tag)
                        _is_new_provisioner = True
                    except etcd.EtcdAlreadyExist:
                        pass
            else:
                if _tag not in NS.node_context.tags and _cnc_is_managed:
                    try:
                        _index_key = "/indexes/tags/%s" % _tag
                        _node_id = json.dumps([NS.node_context.node_id])
                        etcd_utils.write(
                            _index_key, _node_id,
                            prevExist=False
                        )
                        etcd_utils.refresh(_index_key, sync_ttl + 50)
                        tags.append(_tag)
                        _is_new_provisioner = True
                    except etcd.EtcdAlreadyExist:
                        pass

        # updating node context with latest tags
        logger.log(
            "debug",
            NS.publisher_id,
            {"message": "node_sync, updating node context "
                        "data with tags"}
        )
        NS.node_context = NS.tendrl.objects.NodeContext().load()
        current_tags = list(NS.node_context.tags)
        tags += current_tags
        NS.node_context.tags = list(set(tags))
        NS.node_context.tags.sort()
        current_tags.sort()
        if NS.node_context.tags != current_tags:
            NS.node_context.save()

        if "tendrl/monitor" not in tags and \
            NS.tendrl_context.integration_id:
            _cluster = _cluster.load()
            if _is_new_provisioner and _cluster.is_managed == "yes":
                _msg = "node_sync, NEW provisioner node found! "\
                    "re-configuring monitoring (job-id: %s) on this node"
                payload = {
                    "tags": [
                        "tendrl/node_%s" % NS.node_context.node_id
                    ],
                    "run": "tendrl.flows.ConfigureMonitoring",
                    "status": "new",
                    "parameters": {
                        'TendrlContext.integration_id':
                        NS.tendrl_context.integration_id
                    },
                    "type": "node"
                }
                _job_id = str(uuid.uuid4())
                NS.tendrl.objects.Job(
                    job_id=_job_id,
                    status="new",
                    payload=payload
                ).save()
                logger.log(
                    "debug",
                    NS.publisher_id,
                    {"message": _msg % _job_id}
                )

        # Update /indexes/tags/:tag = [node_ids]
        for tag in NS.node_context.tags:

            index_key = "/indexes/tags/%s" % tag
            _node_ids = []
            try:
                _node_ids = etcd_utils.read(index_key).value
                _node_ids = json.loads(_node_ids)
            except etcd.EtcdKeyNotFound:
                pass

            if _node_ids:
                if "provisioner" in tag:
                    # Check if this is a stale provisioner
                    if NS.node_context.node_id != _node_ids[0]:
                        NS.node_context.tags.remove(tag)
                        NS.node_context.save()
                        continue
                if NS.node_context.node_id in _node_ids:
                    if sync_ttl and len(_node_ids) == 1:
                        etcd_utils.refresh(index_key,
                                           sync_ttl + 50)

                    continue
                else:
                    _node_ids += [NS.node_context.node_id]
            else:
                _node_ids = [NS.node_context.node_id]
            _node_ids = list(set(_node_ids))

            etcd_utils.write(index_key, json.dumps(_node_ids))
            if sync_ttl and len(_node_ids) == 1:
                etcd_utils.refresh(index_key, sync_ttl + 50)
        logger.log(
            "debug",
            NS.publisher_id,
            {"message": "node_sync, Updating detected "
             "platform"}
        )
    except Exception as ex:
        Event(
            ExceptionMessage(
                priority="error",
                publisher=NS.publisher_id,
                payload={"message": "node_sync service and indexes "
                                    "sync failed: " + ex.message,
                         "exception": ex}
            )
        )
