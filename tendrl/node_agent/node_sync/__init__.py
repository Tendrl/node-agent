import logging

import etcd
import gevent

from tendrl.commons import sds_sync

from tendrl.node_agent.node_sync import disk_sync
from tendrl.node_agent.node_sync import network_sync

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
                interval = 10
                if NS.first_node_inventory_sync:
                    interval = 2
                    NS.first_node_inventory_sync = False

                gevent.sleep(interval)
                tags = []
                # update node agent service details
                LOG.info("node_sync, Updating Service data")
                for service in TENDRL_SERVICES:
                    s = NS.node_agent.objects.Service(service=service)
                    if s.running:
                        tags.append(TENDRL_SERVICE_TAGS[service.strip("@*")])
                    s.save()
                gevent.sleep(interval)

                # updating node context with latest tags
                LOG.info("node_sync, updating node context data with tags")
                tags = "\n".join(tags)
                NS.node_agent.objects.NodeContext(tags=tags).save()
                gevent.sleep(interval)

                if tendrl_ns.tendrl_context.integration_id:
                    try:
                        tendrl_ns.etcd_orm.client.read(
                            "/clusters/%s" % (
                                tendrl_ns.tendrl_context.integration_id
                            )
                        )
                    except etcd.EtcdKeyNotFound:
                        LOG.error(
                            "Local Tendrl Context with integration id: " +
                            "{} could not be found in central store".format(
                                tendrl_ns.tendrl_context.integration_id
                            )
                        )
                    else:
                        LOG.info(
                            "node_sync, updating node context under clusters"
                        )
                        tendrl_ns.node_agent.objects.ClusterNodeContext(
                            machine_id=tendrl_ns.node_context.machine_id,
                            node_id=tendrl_ns.node_context.node_id,
                            fqdn=tendrl_ns.node_context.fqdn,
                            status=tendrl_ns.node_context.status,
                            tags=tags
                        ).save()
                        gevent.sleep(interval)

                LOG.info("node_sync, Updating OS data")
                NS.node_agent.objects.Os().save()
                gevent.sleep(interval)

                LOG.info("node_sync, Updating cpu")
                NS.node_agent.objects.Cpu().save()
                gevent.sleep(interval)

                LOG.info("node_sync, Updating memory")
                NS.node_agent.objects.Memory().save()
                gevent.sleep(interval)

                LOG.info("node_sync, Updating disks")
                try:
                    NS.etcd_orm.client.delete(
                        ("nodes/%s/Disks") % NS.node_context.node_id,
                        recursive=True)
                except etcd.EtcdKeyNotFound as ex:
                    LOG.debug("Given key is not present in etcd . %s", ex)
                disks = disk_sync.get_node_disks()
                if "disks" in disks:
                    for disk in disks['disks']:
                        NS.node_agent.objects.Disk(**disk).save()
                if "used_disks_id" in disks:
                    for disk in disks['used_disks_id']:
                        NS.etcd_orm.client.write(
                            ("nodes/%s/Disks/used/%s") % (
                                NS.node_context.node_id, disk), "")
                if "free_disks_id" in disks:
                    for disk in disks['free_disks_id']:
                        NS.etcd_orm.client.write(
                            ("nodes/%s/Disks/free/%s") % (
                                NS.node_context.node_id, disk), "")

                LOG.info("node_sync, Updating networks")
                # node wise network
                try:
                    tendrl_ns.etcd_orm.client.delete(
                        ("nodes/%s/Network") % tendrl_ns.node_context.node_id,
                        recursive=True)
                except etcd.EtcdKeyNotFound as ex:
                    LOG.debug("Given key is not present in etcd . %s", ex)
                interfaces = network_sync.get_node_network()
                if len(interfaces) > 0:
                    for interface in interfaces:
                        tendrl_ns.node_agent.objects.NodeNetwork(**interface).save()
                # global network
                try:
                    networks = tendrl_ns.etcd_orm.client.read("/networks")
                    for network in networks.leaves:
                        try:
                            tendrl_ns.etcd_orm.client.delete(("%s/%s") %
                                (network.key, tendrl_ns.node_context.node_id),
                                recursive=True)
                            # it will delete subnet dir when it is empty
                            # if one entry present then deletion never happen
                            tendrl_ns.etcd_orm.client.delete(network.key, dir=True)
                        except etcd.EtcdKeyNotFound as ex:
                            continue
                except etcd.EtcdKeyNotFound as ex:
                    LOG.debug("Given key is not present in etcd . %s", ex)
                if len(interfaces) > 0:
                    for interface in interfaces:
                        if interface["subnet"] is not "":
                            tendrl_ns.node_agent.objects.GlobalNetwork(**interface).save()
                    

            except ValueError as ex:
                LOG.error(ex)

        LOG.info("%s complete" % self.__class__.__name__)
