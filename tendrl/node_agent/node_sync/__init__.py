import logging

import etcd
import gevent

from tendrl.commons import sds_sync

from tendrl.node_agent.node_sync import disk_sync

LOG = logging.getLogger(__name__)


class NodeAgentSyncThread(sds_sync.StateSyncThread):
    def _run(self):
        LOG.info("%s running" % self.__class__.__name__)

        while not self._complete.is_set():
            try:
                gevent.sleep(3)
                tendrl_ns.tendrl_context = tendrl_ns.node_agent.objects\
                    .TendrlContext(tendrl_ns.node_context.node_id)
                tendrl_ns.tendrl_context.save()

                # TODO(team) update node agent service tags here
                LOG.info("node_sync, Updating OS data")
                tendrl_ns.node_agent.objects.Os().save()

                LOG.info("node_sync, Updating cpu")
                tendrl_ns.node_agent.objects.Cpu().save()

                LOG.info("node_sync, Updating memory")
                tendrl_ns.node_agent.objects.Memory().save()

                # TODO(team) update tendrl_context for sds_name and version?

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

                LOG.info("node_sync, Updating Services")
                tendrl_ns.node_agent.objects.Service().save()


            except Exception as ex:
                LOG.error(ex)

        LOG.info("%s complete" % self.__class__.__name__)