import etcd

from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import event_utils


def run():
    try:
        clusters = etcd_utils.read("/clusters")
    except etcd.EtcdKeyNotFound:
        return

    # This logic only runs on node with tag `tendrl/monitor` (tendrl server)
    # So its done checked for all the clusters and tries to set cluster
    # status as `unhealthy` if the status field is missing (due to TTL)
    for cluster in clusters.leaves:
        int_id = cluster.key.split('/')[-1]
        fetched_cluster = NS.tendrl.objects.Cluster(
            integration_id=int_id
        ).load()
        try:
            if fetched_cluster and fetched_cluster.is_managed == "yes":
                NS._int.client.write(
                    "/clusters/{0}/GlobalDetails/status".format(
                        int_id
                    ),
                    "unhealthy",
                    prevExist=False
                )

                cluster_tendrl_context = \
                    NS.tendrl.objects.ClusterTendrlContext(
                        integration_id=int_id
                    ).load()

                msg = "Cluster {0} moved to unhealthy state".format(
                    cluster_tendrl_context.cluster_name
                )
                event_utils.emit_event(
                    "cluster_health_status",
                    "unhealthy",
                    msg,
                    "cluster_{0}".format(
                        cluster_tendrl_context.integration_id
                    ),
                    "WARNING",
                    integration_id=cluster_tendrl_context.integration_id,
                    cluster_name=cluster_tendrl_context.cluster_name,
                    sds_name=cluster_tendrl_context.sds_name
                )
        except etcd.EtcdAlreadyExist:
            pass

    return
