import json

import etcd

from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.message import Message

# TODO(darshan) this has to be moved to Definition file

TENDRL_SERVICES = [
    "tendrl-node-agent",
    "etcd",
    "tendrl-api",
    "tendrl-gluster-integration",
    "tendrl-ceph-integration",
    "glusterd",
    "ceph-mon@*",
    "ceph-osd@*",
    "ceph-installer"
]


def sync():
    try:
        tags = []
        # update node agent service details

        Event(
            Message(
                priority="debug",
                publisher=NS.publisher_id,
                payload={"message": "node_sync, Updating Service data"}
            )
        )
        for service in TENDRL_SERVICES:
            s = NS.tendrl.objects.Service(service=service)
            if s.running:
                service_tag = NS.compiled_definitions.get_parsed_defs()[
                    'namespace.tendrl'
                ]['tags'][service.strip("@*")]
                tags.append(service_tag)
                if "tendrl/node" in service_tag:
                    tags.append("tendrl/node_%s" % NS.node_context.node_id)

                if "tendrl/integration" in service_tag:
                    if NS.tendrl_context.integration_id:
                        tags.append(
                            "tendrl/integration/%s" %
                            NS.tendrl_context.integration_id)

                if service_tag == "tendrl/server":
                    tags.append("tendrl/monitor")
            s.save()

        # updating node context with latest tags
        Event(
            Message(
                priority="debug",
                publisher=NS.publisher_id,
                payload={"message": "node_sync, updating node context "
                                    "data with tags"
                         }
            )
        )
        current_tags = list(NS.node_context.tags)
        tags += current_tags
        NS.node_context.tags = list(set(tags))
        if NS.node_context.tags != current_tags:
            NS.node_context.save()

        # Update /indexes/tags/:tag = [node_ids]
        for tag in NS.node_context.tags:
            index_key = "/indexes/tags/%s" % tag
            _node_ids = []
            try:
                _node_ids = NS._int.client.read(index_key).value
                _node_ids = json.loads(_node_ids)
            except etcd.EtcdKeyNotFound:
                pass

            if _node_ids:
                if NS.node_context.node_id in _node_ids:
                    continue
                else:
                    _node_ids += [NS.node_context.node_id]
            else:
                _node_ids = [NS.node_context.node_id]
            _node_ids = list(set(_node_ids))
            NS._int.wclient.write(index_key,
                                  json.dumps(_node_ids))

        Event(
            Message(
                priority="debug",
                publisher=NS.publisher_id,
                payload={"message": "node_sync, Updating detected "
                                    "platform"
                         }
            )
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
