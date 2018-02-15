from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.utils import log_utils as logger


def sync(sync_ttl):
    try:
        if NS.tendrl_context.integration_id:
            logger.log(
                "debug",
                NS.publisher_id,
                {"message": "node_sync, updating "
                            "cluster tendrl context"}
            )
            NS.tendrl.objects.ClusterTendrlContext(
                integration_id=NS.tendrl_context.integration_id,
                cluster_id=NS.tendrl_context.cluster_id,
                cluster_name=NS.tendrl_context.cluster_name,
                sds_name=NS.tendrl_context.sds_name,
                sds_version=NS.tendrl_context.sds_version
            ).save()
            logger.log(
                "debug",
                NS.publisher_id,
                {"message": "node_sync, Updating"
                            "cluster node context"}
            )
            NS.tendrl.objects.ClusterNodeContext(
                node_id=NS.node_context.node_id,
                fqdn=NS.node_context.fqdn,
                status="UP",
                tags=NS.node_context.tags
            ).save(ttl=sync_ttl)
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
