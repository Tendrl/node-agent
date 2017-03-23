import json
import logging

import etcd
import gevent

from tendrl.commons import sds_sync

from tendrl.node_agent.node_sync import disk_sync
from tendrl.node_agent.node_sync import network_sync
from tendrl.node_agent.node_sync import platform_detect
from tendrl.node_agent.node_sync import sds_detect

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
    "tendrl-ceph-integration": "tendrl/integration/ceph",
    "glusterd": "gluster/server",
    "ceph-mon": "ceph/mon",
    "ceph-osd": "ceph/osd"
}


class NodeAgentSyncThread(sds_sync.StateSyncThread):
    def _run(self):
        LOG.info("%s running", self.__class__.__name__)

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
                    s = NS.tendrl.objects.Service(service=service)
                    if s.running:
                        tags.append(TENDRL_SERVICE_TAGS[service.strip("@*")])
                    s.save()
                gevent.sleep(interval)

                # updating node context with latest tags
                LOG.info("node_sync, updating node context data with tags")
                NS.node_context = NS.node_context.load()
                current_tags = json.loads(NS.node_context.tags)
                tags += current_tags
                NS.tendrl.objects.NodeContext(tags=list(set(tags))).save()
                gevent.sleep(interval)

                if NS.tendrl_context.integration_id:
                    try:
                        NS.etcd_orm.client.read(
                            "/clusters/%s" % (
                                NS.tendrl_context.integration_id
                            )
                        )
                    except etcd.EtcdKeyNotFound:
                        LOG.error(
                            "Local Tendrl Context with integration id: " +
                            "{} could not be found in central store".format(
                                NS.tendrl_context.integration_id
                            )
                        )
                    else:
                        LOG.info(
                            "node_sync, updating node context under clusters"
                        )
                        NS.tendrl.objects.ClusterTendrlContext(
                            integration_id=NS.tendrl_context.integration_id,
                            cluster_id=NS.tendrl_context.cluster_id,
                            cluster_name=NS.tendrl_context.cluster_name,
                        ).save()
                        NS.tendrl.objects.ClusterNodeContext(
                            machine_id=NS.node_context.machine_id,
                            node_id=NS.node_context.node_id,
                            fqdn=NS.node_context.fqdn,
                            status=NS.node_context.status,
                            tags=tags
                        ).save()
                        gevent.sleep(interval)

                LOG.info("node_sync, Updating detected platform")
                platform_detect.load_and_execute_platform_discovery_plugins()

                LOG.info("node_sync, Updating detected Sds")
                sds_detect.load_and_execute_sds_discovery_plugins()

                LOG.info("node_sync, Updating OS data")
                NS.tendrl.objects.Os().save()
                gevent.sleep(interval)

                LOG.info("node_sync, Updating cpu")
                NS.tendrl.objects.Cpu().save()
                gevent.sleep(interval)

                LOG.info("node_sync, Updating memory")
                NS.tendrl.objects.Memory().save()
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
                        NS.tendrl.objects.Disk(**disk).save()
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
                    NS.etcd_orm.client.delete(
                        ("nodes/%s/Network") % NS.node_context.node_id,
                        recursive=True)
                except etcd.EtcdKeyNotFound as ex:
                    LOG.debug("Given key is not present in etcd . %s", ex)
                interfaces = network_sync.get_node_network()
                if len(interfaces) > 0:
                    for interface in interfaces:
                        NS.tendrl.objects.NodeNetwork(**interface).save()
                        if interface['ipv4']:
                            for ipv4 in interface['ipv4']:
                                index_key = "/indexes/ip/%s" % ipv4
                                NS.etcd_orm.client.write(
                                    index_key, NS.node_context.node_id)
                        # TODO(team) add ipv6 support
                        # if interface['ipv6']:
                        #    for ipv6 in interface['ipv6']:
                        #        index_key = "/indexes/ip/%s/%s" % (ipv6,
                        #
                                # NS.node_context.node_id)
                        #        NS.etcd_orm.client.write(index_key, 1)

                # global network
                try:
                    networks = NS.etcd_orm.client.read("/networks")
                    for network in networks.leaves:
                        try:
                            NS.etcd_orm.client.delete(("%s/%s") % (
                                network.key, NS.node_context.node_id),
                                recursive=True)
                            # it will delete subnet dir when it is empty
                            # if one entry present then deletion never happen
                            NS.etcd_orm.client.delete(network.key, dir=True)
                        except (etcd.EtcdKeyNotFound, etcd.EtcdDirNotEmpty):
                            continue
                except etcd.EtcdKeyNotFound as ex:
                    LOG.debug("Given key is not present in etcd . %s", ex)
                if len(interfaces) > 0:
                    for interface in interfaces:
                        if interface["subnet"] is not "":
                            NS.node_agent.objects.GlobalNetwork(
                                **interface).save()

            except Exception as ex:
                LOG.error(ex)

        LOG.info("%s complete", self.__class__.__name__)
