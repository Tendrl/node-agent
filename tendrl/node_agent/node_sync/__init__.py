import etcd
import gevent
import json

from tendrl.commons.event import Event
from tendrl.commons.message import Message, ExceptionMessage

from tendrl.commons import sds_sync

from tendrl.node_agent.node_sync import disk_sync
from tendrl.node_agent.node_sync import network_sync
from tendrl.node_agent.node_sync import platform_detect
from tendrl.node_agent.node_sync import sds_detect

# TODO(darshan) this has to be moved to Definition file

TENDRL_SERVICES = [
    "tendrl-node-agent",
    "etcd",
    "tendrl-apid",
    "tendrl-gluster-integration",
    "tendrl-ceph-integration",
    "glusterd",
    "ceph-mon@*",
    "ceph-osd@*",
    "ceph-installer"
]


class NodeAgentSyncThread(sds_sync.StateSyncThread):
    def _run(self):
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "%s running" % self.__class__.__name__}
            )
        )
        while not self._complete.is_set():
            try:
                NS.tendrl_context = NS.tendrl_context.load()
                priority = "debug"
                interval = 8
                if NS.first_node_inventory_sync:
                    interval = 2
                    priority = "info"
                    NS.first_node_inventory_sync = False

                gevent.sleep(interval)
                tags = []
                # update node agent service details
                Event(
                    Message(
                        priority=priority,
                        publisher=NS.publisher_id,
                        payload={"message": "node_sync, Updating Service data"}
                    )
                )
                for service in TENDRL_SERVICES:
                    s = NS.tendrl.objects.Service(service=service)
                    if s.running:
                        service_tag = NS.compiled_definitions.get_parsed_defs()[
                            'namespace.tendrl'
                        ]['tags'][service.strip("@*")]
                        tags.append(service_tag)
                        if "tendrl/integration" in service_tag:
                            if NS.tendrl_context.integration_id:
                                tags.append("tendrl/integration/%s" % NS.tendrl_context.integration_id)
                        if service_tag == "tendrl/server":
                            tags.append("tendrl/monitor")
                    s.save()                    
                gevent.sleep(interval)

                # updating node context with latest tags
                Event(
                    Message(
                        priority=priority,
                        publisher=NS.publisher_id,
                        payload={"message": "node_sync, updating node context "
                                            "data with tags"
                                 }
                    )
                )
                NS.node_context = NS.node_context.load()
                current_tags = json.loads(NS.node_context.tags)
                tags += current_tags
                NS.node_context.tags = list(set(tags))
                if NS.node_context.tags != current_tags:
                    NS.node_context.save()
                
                # Update /indexes/tags/:tag = [node_ids]
                for tag in NS.node_context.tags:
                    index_key = "/indexes/tags/%s" % tag
                    _node_ids = []
                    try:
                        _node_ids = NS._int.client.read(index_key).value
                        _node_ids = json.loads(_node_ids)
                    except etcd.EtcdKeyNotFound:
                        pass

                    if _node_ids:
                        if NS.node_context.node_id in _node_ids:
                            continue
                        else:
                            _node_ids += [NS.node_context.node_id]
                    else:
                        _node_ids = [NS.node_context.node_id]
                    _node_ids = list(set(_node_ids))
                    NS._int.wclient.write(index_key,
                                          json.dumps(_node_ids))
                        
                gevent.sleep(interval)
                # Check if Node is part of any Tendrl imported/created sds cluster
                try:
                    Event(
                        Message(
                            priority=priority,
                            publisher=NS.publisher_id,
                            payload={"message": "Refresh /indexes/machine_id/%s == Node %s" % (
                                NS.node_context.machine_id,
                                NS.node_context.node_id)
                                     }
                        )
                    )

                    index_key = "/indexes/machine_id/%s" % NS.node_context.machine_id
                    NS._int.wclient.write(index_key, NS.node_context.node_id,
                                          prevExist=False)

                except etcd.EtcdKeyNotFound:
                    pass

                if NS.tendrl_context.integration_id:
                    try:
                        NS._int.client.read(
                            "/clusters/%s" % (
                                NS.tendrl_context.integration_id
                            )
                        )
                        Event(
                        Message(
                            priority=priority,
                            publisher=NS.publisher_id,
                            payload={"message": "Node %s is part of sds "
                                                "cluster %s" % (
                                NS.node_context.node_id,
                                NS.tendrl_context.integration_id)
                                     }
                        )
                    )

                    except etcd.EtcdKeyNotFound:
                        Event(
                            Message(
                                priority="warning",
                                publisher=NS.publisher_id,
                                payload={"message": "Node %s is not part of "
                                                    "any sds cluster" %
                                                    NS.node_context.node_id
                                         }
                            )
                        )
                    else:                        
                        Event(
                            Message(
                                priority=priority,
                                publisher=NS.publisher_id,
                                payload={"message": "node_sync, updating "
                                                    "cluster tendrl context"
                                         }
                            )
                        )

                        NS.tendrl.objects.ClusterTendrlContext(
                            integration_id=NS.tendrl_context.integration_id,
                            cluster_id=NS.tendrl_context.cluster_id,
                            cluster_name=NS.tendrl_context.cluster_name,
                            sds_name=NS.tendrl_context.sds_name,
                            sds_version=NS.tendrl_context.sds_version
                        ).save()
                        Event(
                            Message(
                                priority=priority,
                                publisher=NS.publisher_id,
                                payload={"message": "node_sync, Updating"
                                                    "cluster node context"
                                         }
                            )
                        )
                        NS.tendrl.objects.ClusterNodeContext(
                            machine_id=NS.node_context.machine_id,
                            node_id=NS.node_context.node_id,
                            fqdn=NS.node_context.fqdn,
                            status=NS.node_context.status,
                            tags=NS.node_context.tags
                        ).save()
                        gevent.sleep(interval)

                Event(
                    Message(
                        priority=priority,
                        publisher=NS.publisher_id,
                        payload={"message": "node_sync, Updating detected "
                                            "platform"
                                 }
                    )
                )
                platform_detect.load_and_execute_platform_discovery_plugins()

                Event(
                    Message(
                        priority=priority,
                        publisher=NS.publisher_id,
                        payload={"message": "node_sync, Updating detected Sds"}
                    )
                )
                sds_detect.load_and_execute_sds_discovery_plugins()

                Event(
                    Message(
                        priority=priority,
                        publisher=NS.publisher_id,
                        payload={"message": "node_sync, Updating OS data"}
                    )
                )
                NS.tendrl.objects.Os().save()
                gevent.sleep(interval)

                Event(
                    Message(
                        priority=priority,
                        publisher=NS.publisher_id,
                        payload={"message": "node_sync, Updating cpu"}
                    )
                )
                NS.tendrl.objects.Cpu().save()
                gevent.sleep(interval)

                Event(
                    Message(
                        priority=priority,
                        publisher=NS.publisher_id,
                        payload={"message": "node_sync, Updating memory"}
                    )
                )
                NS.tendrl.objects.Memory().save()
                gevent.sleep(interval)

                Event(
                    Message(
                        priority=priority,
                        publisher=NS.publisher_id,
                        payload={"message": "node_sync, Updating disks"}
                    )
                )
                disks = disk_sync.get_node_disks()
                try:
                    all_disk_id = []
                    all_disk_id.extend(disks["used_disks_id"])
                    all_disk_id.extend(disks["free_disks_id"])
                    if all_disk_id:
                        all_disk = NS._int.client.read(
                            ("nodes/%s/Disks/all") % NS.node_context.node_id)
                        for disk in all_disk.leaves:
                            did = disk.key.split('/')[-1]
                            if did not in all_disk_id:
                                NS._int.wclient.delete(
                                    ("nodes/%s/Disks/all/%s") %
                                        (NS.node_context.node_id, did), recursive=True)
                                try:
                                    NS._int.wclient.delete(
                                    ("nodes/%s/Disks/used/%s") %
                                        (NS.node_context.node_id, did))
                                except etcd.EtcdKeyNotFound as ex:
                                    pass

                                try:
                                    NS._int.wclient.delete(
                                    ("nodes/%s/Disks/free/%s") %
                                        (NS.node_context.node_id, did))
                                except etcd.EtcdKeyNotFound as ex:
                                    pass
                except etcd.EtcdKeyNotFound as ex:
                    Event(
                        ExceptionMessage(
                            priority="debug",
                            publisher=NS.publisher_id,
                            payload={"message": "Given key is not present in "
                                                "etcd .",
                                                "exception": ex
                                     }
                        )
                    )
                if "disks" in disks:
                    for disk in disks['disks']:
                        NS.tendrl.objects.Disk(**disk).save()
                if "used_disks_id" in disks:
                    for disk in disks['used_disks_id']:
                        NS._int.wclient.write(
                            ("nodes/%s/Disks/used/%s") % (
                                NS.node_context.node_id, disk), "")
                if "free_disks_id" in disks:
                    for disk in disks['free_disks_id']:
                        NS._int.wclient.write(
                            ("nodes/%s/Disks/free/%s") % (
                                NS.node_context.node_id, disk), "")

                Event(
                    Message(
                        priority=priority,
                        publisher=NS.publisher_id,
                        payload={"message": "node_sync, Updating networks"}
                    )
                )
                # node wise network
                try:
                    NS._int.wclient.delete(
                        ("nodes/%s/Network") % NS.node_context.node_id,
                        recursive=True)
                except etcd.EtcdKeyNotFound as ex:
                    Event(
                        ExceptionMessage(
                            priority="debug",
                            publisher=NS.publisher_id,
                            payload={"message": "Given key is not present in "
                                                "etcd .",
                                     "exception": ex
                                     }
                        )
                    )
                interfaces = network_sync.get_node_network()
                if len(interfaces) > 0:
                    for interface in interfaces:
                        NS.tendrl.objects.NodeNetwork(**interface).save()
                        if interface['ipv4']:
                            for ipv4 in interface['ipv4']:
                                index_key = "/indexes/ip/%s" % ipv4
                                NS._int.wclient.write(
                                    index_key, NS.node_context.node_id,
                                    prevExist=False)
                        # TODO(team) add ipv6 support
                        # if interface['ipv6']:
                        #    for ipv6 in interface['ipv6']:
                        #        index_key = "/indexes/ip/%s/%s" % (ipv6,
                        #
                                # NS.node_context.node_id)
                        #        NS._int.wclient.write(index_key, 1)

                # global network
                try:
                    networks = NS._int.client.read("/networks")
                    for network in networks.leaves:
                        try:
                            NS._int.wclient.delete(("%s/%s") % (
                                network.key, NS.node_context.node_id),
                                recursive=True)
                            # it will delete subnet dir when it is empty
                            # if one entry present then deletion never happen
                            NS._int.wclient.delete(network.key, dir=True)
                        except (etcd.EtcdKeyNotFound, etcd.EtcdDirNotEmpty):
                            continue
                except etcd.EtcdKeyNotFound as ex:
                    Event(
                        ExceptionMessage(
                            priority="debug",
                            publisher=NS.publisher_id,
                            payload={"message": "Given key is not present in "
                                                "etcd .",
                                     "exception": ex
                                     }
                        )
                    )
                if len(interfaces) > 0:
                    for interface in interfaces:
                        if interface["subnet"] is not "":
                            NS.node_agent.objects.GlobalNetwork(
                                **interface).save()

            except Exception as ex:
                Event(
                    ExceptionMessage(
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={"message": "node_sync failed: " + ex.message,
                                 "exception": ex}
                    )
                )
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "%s complete" % self.__class__.__name__}
            )
        )
