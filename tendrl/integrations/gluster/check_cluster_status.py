import etcd

from tendrl.commons.utils import etcd_utils


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
        except etcd.EtcdAlreadyExist:
            pass

    return
