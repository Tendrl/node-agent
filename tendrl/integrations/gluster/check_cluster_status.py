import etcd

from tendrl.commons.utils import etcd_utils


def run():
    try:
        clusters = etcd_utils.read("/clusters")
    except etcd.EtcdKeyNotFound:
        return

    # This logic only runs on node with tag `tendrl/monitor` (tendrl server)
    for cluster in clusters.leaves:
        int_id = cluster.key.split('/')[-1]
        fetched_cluster = NS.tendrl.objects.Cluster(
            integration_id=int_id
        ).load()
        if fetched_cluster and fetched_cluster.is_managed == "yes":
            try:
                from tendrl.gluster_integration.objects.global_details import \
                    GlobalDetails
                _gc = GlobalDetails(integration_id=int_id).load()
                _gc.watch_attrs()
            except ImportError:
                pass


    return
