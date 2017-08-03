import etcd

from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.message import Message


def sync():
    try:
        if NS.tendrl_context.integration_id:
            try:
                NS._int.client.read(
                    "/clusters/%s" % (
                        NS.tendrl_context.integration_id
                    )
                )
                Event(
                    Message(
                        priority="debug",
                        publisher=NS.publisher_id,
                        payload={"message": "Node %s is part of sds "
                                            "cluster %s" %
                                            (NS.node_context.node_id,
                                             NS.tendrl_context.integration_id)
                                 }
                    )
                )

            except etcd.EtcdKeyNotFound:
                Event(
                    Message(
                        priority="debug",
                        publisher=NS.publisher_id,
                        payload={"message": "Node %s is not part of "
                                            "any sds cluster" %
                                            NS.node_context.node_id
                                 }
                    )
                )
            else:
                Event(
                    Message(
                        priority="debug",
                        publisher=NS.publisher_id,
                        payload={"message": "node_sync, updating "
                                            "cluster tendrl context"
                                 }
                    )
                )

                NS.tendrl.objects.ClusterTendrlContext(
                    integration_id=NS.tendrl_context.integration_id,
                    cluster_id=NS.tendrl_context.cluster_id,
                    cluster_name=NS.tendrl_context.cluster_name,
                    sds_name=NS.tendrl_context.sds_name,
                    sds_version=NS.tendrl_context.sds_version
                ).save()
                Event(
                    Message(
                        priority="debug",
                        publisher=NS.publisher_id,
                        payload={"message": "node_sync, Updating"
                                            "cluster node context"
                                 }
                    )
                )
                NS.tendrl.objects.ClusterNodeContext(
                    node_id=NS.node_context.node_id,
                    fqdn=NS.node_context.fqdn,
                    status=NS.node_context.status,
                    tags=NS.node_context.tags
                ).save()
    except Exception as ex:
        Event(
            ExceptionMessage(
                priority="error",
                publisher=NS.publisher_id,
                payload={"message": "node_sync cluster contexts sync "
                                    "failed: " + ex.message,
                         "exception": ex}
            )
        )
