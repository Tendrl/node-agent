import etcd
import uuid

from tendrl.commons.objects.job import Job
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger


def run():
    try:
        nodes = NS._int.client.read("/nodes")
    except etcd.EtcdKeyNotFound:
        return

    for node in nodes.leaves:
        node_id = node.key.split('/')[-1]
        try:
            NS._int.wclient.write(
                "/nodes/{0}/NodeContext/status".format(node_id),
                "DOWN",
                prevExist=False
            )
            _node_context = NS.tendrl.objects.NodeContext(
                node_id=node_id
            ).load()
            _tc = NS.tendrl.objects.TendrlContext(
                node_id=node_id
            ).load()
            _cluster = NS.tendrl.objects.Cluster(
                integration_id=_tc.integration_id
            ).load()

            # Remove stale provisioner tag
            if _cluster.is_managed == "yes":
                _tag = "provisioner/%s" % _cluster.integration_id
                if _tag in _node_context.tags:
                    _index_key = "/indexes/tags/%s" % _tag
                    _node_context.tags.remove(_tag)
                    _node_context.save()
                    etcd_utils.delete(_index_key)
                    _msg = "node_sync, STALE provisioner node "\
                        "found! re-configuring monitoring "\
                        "(job-id: %s) on this node"
                    payload = {
                        "tags": ["tendrl/node_%s" % node_id],
                        "run": "tendrl.flows.ConfigureMonitoring",
                        "status": "new",
                        "parameters": {
                            'TendrlContext.integration_id': _tc.integration_id
                        },
                        "type": "node"
                    }
                    _job_id = str(uuid.uuid4())
                    Job(
                        job_id=_job_id,
                        status="new",
                        payload=payload
                    ).save()
                    logger.log(
                        "debug",
                        NS.publisher_id,
                        {"message": _msg % _job_id}
                    )
        except etcd.EtcdAlreadyExist:
            pass
    return
