import json
import logging
import signal
import socket
import time

import gevent.event
import gevent.greenlet
import pull_hardware_inventory

from tendrl.common.config import TendrlConfig
from tendrl.common.log import setup_logging
from tendrl.common.manager.manager import Manager
from tendrl.common.manager.manager import SyncStateThread
from tendrl.node_agent.persistence.tendrl_definitions import TendrlDefinitions

config = TendrlConfig("node_agent", "/etc/tendrl/tendrl.conf")

from tendrl.node_agent.manager.tendrl_definitions_node_agent import data as \
    def_data
from tendrl.node_agent.manager import utils
from tendrl.node_agent.persistence.cpu import Cpu
from tendrl.node_agent.persistence.memory import Memory
from tendrl.node_agent.persistence.node import Node
from tendrl.node_agent.persistence.node_context import NodeContext
from tendrl.node_agent.persistence.os import Os
from tendrl.node_agent.persistence.persister import NodeAgentEtcdPersister
from tendrl.node_agent.persistence.tendrl_context import TendrlContext

LOG = logging.getLogger(__name__)
HARDWARE_INVENTORY_FILE = "/etc/tendrl/tendrl-node-inventory.json"


class NodeAgentSyncStateThread(SyncStateThread):

    def __init__(self, manager):
        super(NodeAgentSyncStateThread, self).__init__(manager)

        self._manager = manager
        self._complete = gevent.event.Event()

    def _run(self):
        LOG.info("%s running" % self.__class__.__name__)

        while not self._complete.is_set():
            try:
                gevent.sleep(3)
                node_inventory = pull_hardware_inventory.get_node_inventory()
                # try to check if the hardware inventory has changed from the
                # previous check.
                LOG.info("Hardware inventory pulled successfully")
                try:
                    with open(HARDWARE_INVENTORY_FILE) as f:
                        raw_data = json.loads(f.read())
                except IOError:
                    raw_data = {}
                    LOG.info("No earlier hardware inventory data found")
                else:
                    # if the node inventory has not changed, just end this
                    # iteration
                    if raw_data == node_inventory:
                        LOG.debug("Hardware inventory not changed,"
                                  " since the previous run")
                        continue

                # updating the latest node inventory to the file.
                with open(HARDWARE_INVENTORY_FILE, 'w') as fp:
                    json.dump(node_inventory, fp)

                LOG.info("change detected in node hardware inventory,"
                         " trying to update the latest changes")

                LOG.debug("raw_data: %s\n\n hardware inventory: %s" % (
                    raw_data, node_inventory))

                self._manager.on_pull(node_inventory)
            except Exception as ex:
                LOG.error(ex)

        LOG.info("%s complete" % self.__class__.__name__)


class NodeAgentManager(Manager):
    """manage user request thread

    """

    def __init__(self, machine_id):
        self._complete = gevent.event.Event()
        self._discovery_thread = NodeAgentSyncStateThread(self)
        super(
            NodeAgentManager,
            self
        ).__init__(
            "node",
            utils.get_node_context(),
            config,
            self._discovery_thread,
            NodeAgentEtcdPersister(config),
            "/tendrl_definitions_node_agent/data"
        )
        self.register_node(machine_id)

    def register_node(self, machine_id):
        local_node_context = utils.get_local_node_context()
        if local_node_context:
            if utils.get_node_context(self.etcd_client, local_node_context) \
                    is None:
                utils.delete_local_node_context()

        self.persister.update_node_context(
            NodeContext(
                updated=str(time.time()),
                machine_id=machine_id,
                node_id=utils.set_local_node_context(),
                fqdn=socket.getfqdn(),
            )
        )
        tendrl_context = pull_hardware_inventory.getTendrlContext()
        self.persister.update_tendrl_context(
            TendrlContext(
                updated=str(time.time()),
                sds_version=tendrl_context['sds_version'],
                node_id=utils.get_local_node_context(),
                sds_name=tendrl_context['sds_name'],
            )
        )

        self.persister.update_node(
            Node(
                node_id=utils.get_local_node_context(),
                fqdn=socket.getfqdn(),
                status="UP"
            )
        )
        self.persister.update_tendrl_definitions(TendrlDefinitions(
            updated=str(time.time()), data=def_data))

    def on_pull(self, raw_data):
        LOG.info("on_pull, Updating Node_context data")
        self.persister.update_node_context(
            NodeContext(
                updated=str(time.time()),
                machine_id=raw_data["machine_id"],
                node_id=raw_data["node_id"],
                fqdn=raw_data["os"]["FQDN"],
            )
        )
        LOG.info("on_pull, Updating node data")
        self.persister.update_node(
            Node(
                node_id=raw_data["node_id"],
                fqdn=raw_data["os"]["FQDN"],
                status="UP"
            )
        )
        if "tendrl_context" in raw_data:
            LOG.info("on_pull, Updating tendrl context data")
            tc = raw_data['tendrl_context']
            self.persister.update_tendrl_context(
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
            self.persister.update_os(
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
            self.persister.update_memory(
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
            self.persister.update_cpu(
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


def main():
    setup_logging(
        config.get('node_agent', 'log_cfg_path'),
        config.get('node_agent', 'log_level')
    )

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
