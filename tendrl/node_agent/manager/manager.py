import etcd
import json
import logging
import signal
import socket
import time

import gevent.event
import gevent.greenlet
import pull_hardware_inventory
from pull_service_status import TENDRL_SERVICE_TAGS

from tendrl.commons import config
from tendrl.commons.log import setup_logging
from tendrl.commons.manager.manager import Manager
from tendrl.commons.manager.manager import SyncStateThread
from tendrl.node_agent.discovery.sds.manager import SDSDiscoveryManager
from tendrl.node_agent.persistence.tendrl_definitions import TendrlDefinitions

from tendrl.node_agent.manager.tendrl_definitions_node_agent import data as \
    def_data
from tendrl.node_agent.manager import utils
from tendrl.node_agent.persistence.cpu import Cpu
from tendrl.node_agent.persistence.disk import Disk
from tendrl.node_agent.persistence.memory import Memory
from tendrl.node_agent.persistence.node import Node
from tendrl.node_agent.persistence.node_context import NodeContext
from tendrl.node_agent.persistence.os import Os
from tendrl.node_agent.persistence.platform import Platform
from tendrl.node_agent.persistence.persister import NodeAgentEtcdPersister
from tendrl.node_agent.persistence.service import Service
from tendrl.node_agent.persistence.tendrl_context import TendrlContext
from tendrl.node_agent.discovery.platform.manager import PlatformManager
from tendrl.node_agent.discovery.platform.base import PlatformDiscoverPlugin

config = config.load_config("node-agent",
                            "/etc/tendrl/node-agent/node-agent.conf.yaml")
LOG = logging.getLogger(__name__)


class NodeAgentSyncStateThread(SyncStateThread):

    def __init__(self, manager):
        super(NodeAgentSyncStateThread, self).__init__(manager)

        self._manager = manager
        self._complete = gevent.event.Event()
        self.current_hw_data = None

    def _run(self):
        LOG.info("%s running" % self.__class__.__name__)

        while not self._complete.is_set():
            try:
                gevent.sleep(3)
                node_inventory = pull_hardware_inventory.get_node_inventory()
                # try to check if the hardware inventory has changed from the
                # previous check.
                LOG.info("Hardware inventory pulled successfully")
                # if the node inventory has not changed, just end this
                # iteration
                if self.current_hw_data == node_inventory:
                    LOG.debug("Hardware inventory not changed,"
                              " since the previous run")
                    continue

                # updating the latest node inventory to the file.
                self.current_hw_data = node_inventory

                LOG.info("change detected in node hardware inventory,"
                         " trying to update the latest changes")

                LOG.debug("raw_data: %s\n\n hardware inventory: %s" % (
                    self.current_hw_data, node_inventory))

                self._manager.on_pull(node_inventory)
            except Exception as ex:
                LOG.error(ex)

        LOG.info("%s complete" % self.__class__.__name__)


def update_node_context(manager, machine_id, tags=""):
    manager.persister_thread.update_node_context(
        NodeContext(
            updated=str(time.time()),
            machine_id=machine_id,
            node_id=utils.set_local_node_context(),
            fqdn=socket.getfqdn(),
            tags=tags
        )
    )


class NodeAgentManager(Manager):
    """manage user request thread

    """

    def __init__(self, machine_id):
        self._complete = gevent.event.Event()
        # Initialize the state sync thread which gets the underlying
        # node details and pushes the same to etcd
        etcd_kwargs = {'port': int(config.get("commons", "etcd_port")),
                       'host': config.get("commons", "etcd_connection")}
        self.etcd_client = etcd.Client(**etcd_kwargs)
        local_node_context = utils.set_local_node_context()
        if local_node_context:
            if utils.get_node_context(self.etcd_client, local_node_context) \
                    is None:
                utils.delete_local_node_context()

        node_id = utils.get_local_node_context()
        super(
            NodeAgentManager,
            self
        ).__init__(
            "node",
            node_id,
            config,
            NodeAgentSyncStateThread(self),
            NodeAgentEtcdPersister(config),
            "/tendrl_definitions_node_agent/data",
            node_id=node_id
        )
        self.register_node(machine_id)
        self.load_and_execute_platform_discovery_plugins()
        self.load_and_execute_sds_discovery_plugins()

    def register_node(self, machine_id):
        update_node_context(self, machine_id)
        tendrl_context = pull_hardware_inventory.getTendrlContext()
        self.persister_thread.update_tendrl_context(
            TendrlContext(
                updated=str(time.time()),
                sds_version=tendrl_context['sds_version'],
                node_id=utils.get_local_node_context(),
                sds_name=tendrl_context['sds_name'],
            )
        )

        self.persister_thread.update_node(
            Node(
                node_id=utils.get_local_node_context(),
                fqdn=socket.getfqdn(),
                status="UP"
            )
        )
        self.persister_thread.update_tendrl_definitions(TendrlDefinitions(
            updated=str(time.time()), data=def_data))

    def on_pull(self, raw_data):
        LOG.info("on_pull, Updating Node_context data")
        # Updating the Tags of the node, tags are based on
        # services running on the node
        tags = [
            TENDRL_SERVICE_TAGS[s] for s in raw_data[
                "services"
            ].iterkeys() if raw_data["services"][s]["running"]
        ]

        tag_set = set(tags)
        tags = ",".join(tag_set)
        update_node_context(self, utils.get_machine_id(), tags)
        
        LOG.info("on_pull, Updating node data")
        self.persister_thread.update_node(
            Node(
                node_id=raw_data["node_id"],
                fqdn=raw_data["os"]["FQDN"],
                status="UP"
            )
        )
        if "tendrl_context" in raw_data:
            LOG.info("on_pull, Updating tendrl context data")
            tc = raw_data['tendrl_context']
            self.persister_thread.update_tendrl_context(
                TendrlContext(
                    updated=str(time.time()),
                    sds_name=tc["sds_name"],
                    sds_version=tc["sds_version"],
                    node_id=raw_data["node_id"],
                )
            )
            LOG.info("on_pull, Updated tendrl context data successfully")

        if "os" in raw_data:
            LOG.info("on_pull, Updating OS data")
            node = raw_data['os']
            self.persister_thread.update_os(
                Os(
                    updated=str(time.time()),
                    os=node["Name"],
                    os_version=node["OSVersion"],
                    kernel_version=node["KernelVersion"],
                    selinux_mode=node["SELinuxMode"],
                    node_id=raw_data["node_id"],
                )
            )
        if "memory" in raw_data:
            LOG.info("on_pull, Updating memory")
            memory = raw_data['memory']
            self.persister_thread.update_memory(
                Memory(
                    updated=str(time.time()),
                    total_size=memory["TotalSize"],
                    total_swap=memory["SwapTotal"],
                    node_id=raw_data["node_id"],
                )
            )
        if "cpu" in raw_data:
            LOG.info("on_pull, Updating cpu")
            cpu = raw_data['cpu']
            self.persister_thread.update_cpu(
                Cpu(
                    updated=str(time.time()),
                    model=cpu["Model"],
                    vendor_id=cpu["VendorId"],
                    model_name=cpu["ModelName"],
                    architecture=cpu["Architecture"],
                    cores_per_socket=cpu["CoresPerSocket"],
                    cpu_op_mode=cpu["CpuOpMode"],
                    cpu_family=cpu["CPUFamily"],
                    cpu_count=cpu["CPUs"],
                    node_id=raw_data["node_id"],
                )
            )
        if "disks" in raw_data:
            LOG.info("on_pull, Updating disks")
            try:
                self.etcd_client.delete(
                    ("nodes/%s/Disks") % raw_data["node_id"], recursive=True)
            except etcd.EtcdKeyNotFound as ex:
                LOG.debug("Given key is not present in etcd . %s", ex)
            disks = raw_data['disks']
            if "disks" in disks:
                for disk in disks['disks']:
                    disk['node_id'] = raw_data['node_id']
                    disk_obj = Disk(disk)
                    disk_json = disk_obj.to_json_string()
                    self.etcd_client.write((disk_obj.__name__) % (
                        raw_data["node_id"], disk['disk_id']), disk_json)
            if "used_disks_id" in disks:
                for disk in disks['used_disks_id']:
                    self.etcd_client.write(("nodes/%s/Disks/used/%s") % (
                        raw_data["node_id"], disk), "")
            if "free_disks_id" in disks:
                for disk in disks['free_disks_id']:
                    self.etcd_client.write(("nodes/%s/Disks/free/%s") % (
                        raw_data["node_id"], disk), "")
        if "services" in raw_data:
            LOG.info("on_pull, Updating services")
            try:
                self.etcd_client.delete(
                    ("nodes/%s/Services") % raw_data["node_id"],
                    recursive=True)
            except etcd.EtcdKeyNotFound as ex:
                LOG.debug("Given key is not present in etcd . %s", ex)

            for service, value in raw_data["services"].iteritems():
                self.persister_thread.update_service(
                    Service(
                        updated=str(time.time()),
                        exists=value["exists"],
                        running=value["running"],
                        node_id=raw_data["node_id"],
                        service=service
                    )
                )

    def load_and_execute_platform_discovery_plugins(self):
        # platform plugins
        LOG.info("load_and_execute_platform_discovery_plugins, platform \
         plugins")
        try:
            pMgr = PlatformManager()
        except ValueError as ex:
            LOG.error(
                'Failed to init PlatformManager. \Error %s' % str(ex))
            return
        # execute the platform plugins
        for plugin in pMgr.get_available_plugins():
            platform_details = plugin.discover_platform()
            if len(platform_details.keys()) > 0:
                # update etcd
                try:
                    self.persister_thread.update_platform(
                        Platform(
                            updated=str(time.time()),
                            os=platform_details["Name"],
                            os_version=platform_details["OSVersion"],
                            kernel_version=platform_details["KernelVersion"],
                            node_id=utils.get_local_node_context(),
                        )
                    )
                except etcd.EtcdException as ex:
                    LOG.error(
                        'Failed to update etcd . \Error %s' % str(ex))
                break

    def load_and_execute_sds_discovery_plugins(self):
        LOG.info("load_and_execute_sds_discovery_plugins")
        try:
            sds_discovery_manager = SDSDiscoveryManager()
        except ValueError as ex:
            LOG.error(
                'Failed to init SDSDiscoveryManager. \Error %s' % str(ex))
            return

        # Execute the SDS discovery plugins and tag the nodes with data
        for plugin in sds_discovery_manager.get_available_plugins():
            sds_details = plugin.discover_storage_system()
            if len(sds_details.keys()) > 0:
                dict = {}
                for key in sds_details['cluster_attrs'].keys():
                    dict[key] = sds_details['cluster_attrs'][key]
                try:
                    self.persister_thread.update_node_context(
                        NodeContext(
                            updated=str(time.time()),
                            node_id=utils.get_local_node_context(),
                            sds_pkg_name=sds_details['pkg_name'],
                            sds_pkg_version=sds_details['pkg_version'],
                            detected_cluster_id=sds_details[
                                'detected_cluster_id'
                            ],
                            cluster_attrs=dict
                        )
                    )
                except etcd.EtcdException as ex:
                    LOG.error('Failed to update etcd . \Error %s' % str(ex))
                break


def main():
    setup_logging(
        config['log_cfg_path'],
        config['log_level']
    )
# init definitions
# init manager and object tree from etcd
    machine_id = utils.get_machine_id()

    m = NodeAgentManager(machine_id)
    m.start()

    complete = gevent.event.Event()

    def shutdown():
        LOG.info("Signal handler: stopping")
        complete.set()

    gevent.signal(signal.SIGTERM, shutdown)
    gevent.signal(signal.SIGINT, shutdown)

    while not complete.is_set():
        complete.wait(timeout=1)


if __name__ == "__main__":
    main()
