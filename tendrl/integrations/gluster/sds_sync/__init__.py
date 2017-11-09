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
                time.sleep(int(NS.config.data.get("sync_interval", 10)))
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

                    bricks_marked_already = True
                    for brick in bricks.leaves:
                        brick_status = NS._int.client.read(
                            "{0}/status".format(brick.key)
                        ).value
                        if brick_status != "Stopped":
                            bricks_marked_already = False
                            break

                    if bricks_marked_already:
                        continue

                    self.update_brick_status(
                        node_context.fqdn,
                        tendrl_context.integration_id,
                        "Stopped"
                    )
                except etcd.EtcdKeyNotFound:
                    pass
                
            time.sleep(_sleep)

    def update_brick_status(self, fqdn, integration_id, status):
        _job_id = str(uuid.uuid4())
        _params = {
            "TendrlContext.integration_id": integration_id,
            "Node.fqdn": fqdn,
            "Brick.status": status
        }
        _job_payload = {
            "tags": [
                "tendrl/integration/{0}".format(
                    integration_id
                )
            ],
            "run": "gluster.flows.UpdateBrickStatus",
            "status": "new",
            "parameters": _params,
            "type": "sds"
        }
        Job(
            job_id=_job_id,
            status="new",
            payload=_job_payload
        ).save()
