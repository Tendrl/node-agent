import logging

import etcd
import gevent

from tendrl.commons import sds_sync

from tendrl.node_agent.node_sync import disk_sync

LOG = logging.getLogger(__name__)

# TODO(darshan) this has to be moved to Definition file

TENDRL_SERVICES = [
    "tendrl-node-agent",
    "etcd",
    "tendrl-apid",
    "tendrl-gluster-integration",
    "tendrl-ceph-integration",
    "glusterd",
    "ceph-mon@*",
    "ceph-osd@*"
]

TENDRL_SERVICE_TAGS = {
    "tendrl-node-agent": "tendrl/node",
    "etcd": "tendrl/central-store",
    "tendrl-apid": "tendrl/server",
    "tendrl-gluster-integration": "tendrl/integration/gluster",
    "tendrl-ceph-integration": "tendrl/integration/gluster",
    "glusterd": "gluster/server",
    "ceph-mon": "ceph/mon",
    "ceph-osd": "ceph/osd"
}


class NodeAgentSyncThread(sds_sync.StateSyncThread):
    def _run(self):
        LOG.info("%s running" % self.__class__.__name__)

        while not self._complete.is_set():
            try:
                gevent.sleep(3)
                tags = []
                # update node agent service details
                LOG.info("node_sync, Updating Service data")
                for service in TENDRL_SERVICES:
                    s = tendrl_ns.node_agent.objects.Service(service=service)
                    if s.running:
                        tags.append(TENDRL_SERVICE_TAGS[service.strip("@*")])
                    s.save()

                # updating node context with latest tags
                LOG.info("node_sync, updating node context data with tags")
                tags = "\n".join(tags)
                tendrl_ns.node_agent.objects.NodeContext(tags=tags).save()

                LOG.info("node_sync, Updating OS data")
                tendrl_ns.node_agent.objects.Os().save()

                LOG.info("node_sync, Updating cpu")
                tendrl_ns.node_agent.objects.Cpu().save()

                LOG.info("node_sync, Updating memory")
                tendrl_ns.node_agent.objects.Memory().save()

                LOG.info("node_sync, Updating disks")
                try:
                    tendrl_ns.etcd_orm.client.delete(
                        ("nodes/%s/Disks") % tendrl_ns.node_context.node_id,
                        recursive=True)
                except etcd.EtcdKeyNotFound as ex:
                    LOG.debug("Given key is not present in etcd . %s", ex)
                disks = disk_sync.get_node_disks()
                if "disks" in disks:
                    for disk in disks['disks']:
                        tendrl_ns.node_agent.objects.Disk(**disk).save()
                if "used_disks_id" in disks:
                    for disk in disks['used_disks_id']:
                        tendrl_ns.etcd_orm.client.write(
                            ("nodes/%s/Disks/used/%s") % (
                                tendrl_ns.node_context.node_id, disk), "")
                if "free_disks_id" in disks:
                    for disk in disks['free_disks_id']:
                        tendrl_ns.etcd_orm.client.write(
                            ("nodes/%s/Disks/free/%s") % (
                                tendrl_ns.node_context.node_id, disk), "")

            except Exception as ex:
                LOG.error(ex)

        LOG.info("%s complete" % self.__class__.__name__)
