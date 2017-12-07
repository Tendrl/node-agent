import etcd
import time

from tendrl.commons.objects.job import Job
from tendrl.commons import sds_sync
from tendrl.commons.utils import log_utils as logger

import uuid


class GlusterIntegrtaionsSyncThread(sds_sync.StateSyncThread):
    def run(self):
        logger.log(
            "debug",
            NS.get("publisher_id", None),
            {"message": "%s running" % self.__class__.__name__}
        )
        _sleep = 0
        while not self._complete.is_set():
            if _sleep > 5:
                _sleep = int(NS.config.data.get("sync_interval", 10))
            else:
                _sleep += 1
            try:
                nodes = NS._int.client.read("/nodes")
            except etcd.EtcdKeyNotFound:
                time.sleep(_sleep)
                continue

            for node in nodes.leaves:
                node_id = node.key.split('/')[-1]
                try:
                    node_context = NS.tendrl.objects.NodeContext(
                        node_id=node_id
                    ).load()
                    tendrl_context = NS.tendrl.objects.TendrlContext(
                        node_id=node_id
                    ).load()

                    if node_context.status != "DOWN" or\
                       tendrl_context.sds_name != "gluster":
                        continue

                    # check if the node belongs to a cluster that is managed

                    cluster = NS.tendrl.objects.Cluster(
                        integration_id=tendrl_context.integration_id
                    ).load()
                    if cluster.is_managed != "yes":
                        continue

                    # check if the bricks of this node are already
                    # marked as down

                    bricks = NS._int.client.read(
                        "clusters/{0}/Bricks/all/{1}".format(
                            tendrl_context.integration_id,
                            node_context.fqdn
                        )
                    )

                    for brick in bricks.leaves:
                        try:
                            NS._int.wclient.write("{0}/status".format(brick.key),
                                                  "Stopped")
                        except (etcd.EtcdAlreadyExist, etcd.EtcdKeyNotFound):
                            pass
                        
                except etcd.EtcdKeyNotFound:
                    pass
                
            time.sleep(_sleep)
