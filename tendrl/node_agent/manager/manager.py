import logging
import signal
import socket

import gevent.event
import gevent.greenlet
import json
import pull_hardware_inventory
from rpc import EtcdThread
from tendrl.bridge_common.log import setup_logging

from tendrl.node_agent.config import TendrlConfig
config = TendrlConfig()

from tendrl.node_agent.manager.command import Command
from tendrl.node_agent.manager import utils
from tendrl.node_agent.persistence.cpu import Cpu
from tendrl.node_agent.persistence.memory import Memory
from tendrl.node_agent.persistence.node import Node
from tendrl.node_agent.persistence.node_context import NodeContext
from tendrl.node_agent.persistence.os import Os
from tendrl.node_agent.persistence.persister import Persister
from tendrl.node_agent.persistence.tendrl_context import TendrlContext
from tendrl.node_agent.persistence.tendrl_definitions import TendrlDefinitions

import time

LOG = logging.getLogger(__name__)
HARDWARE_INVENTORY_FILE = "/etc/tendrl/tendrl-node-inventory.json"


class TopLevelEvents(gevent.greenlet.Greenlet):

    def __init__(self, manager):
        super(TopLevelEvents, self).__init__()

        self._manager = manager
        self._complete = gevent.event.Event()

    def stop(self):
        self._complete.set()

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


class Manager(object):
    """manage user request thread

    """

    def __init__(self, node_id, machine_id):
        self._complete = gevent.event.Event()

        self._user_request_thread = EtcdThread(self)
        self._discovery_thread = TopLevelEvents(self)
        self.persister = Persister()
        self.register_node(node_id, machine_id)

    def stop(self):
        LOG.info("%s stopping" % self.__class__.__name__)
        self._user_request_thread.stop()
        self._discovery_thread.stop()
        self.persister.stop()

    def start(self):
        LOG.info("%s starting" % self.__class__.__name__)
        self._user_request_thread.start()
        self._discovery_thread.start()
        self.persister.start()

    def join(self):
        LOG.info("%s joining" % self.__class__.__name__)
        self._user_request_thread.join()
        self._discovery_thread.join()
        self.persister.join()

    def register_node(self, node_id, machine_id):
        self.persister.update_node_context(
            NodeContext(
                updated=str(time.time()),
                machine_id=machine_id,
                node_id=node_id,
                fqdn=socket.getfqdn(),
            )
        )
        self.persister.update_tendrl_context(
            TendrlContext(
                updated=str(time.time()),
                sds_version="",
                node_id=node_id,
                sds_name="",
                cluster_id=""
            )
        )

        self.persister.update_tendrl_definitions(
            TendrlDefinitions(updated=str(time.time()),
                              data="""---
namespace.tendrl.node_agent:
  object_details:
    Cpu:
      attrs:
        architecture:
          type: String
        cores_per_socket:
          type: String
        cpu_count:
          type: String
        cpu_family:
          type: String
        cpu_op_mode:
          type: String
        model:
          type: String
        model_name:
          type: String
        vendor_id:
          type: String
      enabled: true
      value: /nodes/$node.id/cpu
    Memory:
      attrs:
        total_size:
          type: String
        total_swap:
          type: String
      enabled: true
      value: /nodes/$node.id/memory
    Node:
      atoms:
        cmd:
          enabled: true
          inputs:
            mandatory:
              - Node.cmd_str
          name: "Execute CMD on Node"
          run: tendrl.node_agent.atoms.node.cmd.Cmd
          type: Create
          uuid: dc8fff3a-34d9-4786-9282-55eff6abb6c3
      attrs:
        cmd_str:
          type: String
        fqdn:
          type: String
      enabled: true
      value: /nodes/$node.id/node
    OS:
      attrs:
        kernel_version:
          type: String
        os:
          type: String
        os_varsion:
          type: String
        selinux_mode:
          type: String
      enabled: true
      value: /nodes/$node.id/os
    Package:
      atoms:
        install:
          enabled: true
          inputs:
            mandatory:
              - Package.name
              - Package.pkg_type
            optional:
              - Package.version
          name: "Install Package"
          post_run:
            - tendrl.node_agent.atoms.package.validations.check_package_installed
          run: tendrl.node_agent.atoms.package.install.Install
          type: Create
          uuid: 16abcfd0-aca9-4022-aa0f-5de1c5a742c7
      attrs:
        name:
          help: "Location of the rpm/deb/pypi package"
          type: String
        pkg_type:
          help: "Type of package can be rpm/deb/pip/"
        state:
          help: "State can installed|uninstalled"
        version:
          help: "Version of the rpm/deb/pypi package"
          type: String
      enabled: true
    Process:
      atoms:
        start:
          enabled: true
          inputs:
            mandatory:
              - Service.config_path
              - Service.config_data
          name: "Configure Service"
          post_run:
            - tendrl.node_agent.atoms.service.validations.check_service_running
          run: tendrl.node_agent.atoms.service.configure.Configure
          type: Update
          uuid: b90a0d97-8c9f-4ab1-8f64-dbb5638159a3
      attrs:
        name:
          help: "Name of the service"
          type: String
        state:
          help: "Service state can be started|stopped|restarted|reloaded"
          type: String
      enabled: true
    Service:
      atoms:
        configure:
          enabled: true
          inputs:
            mandatory:
              - Service.config_path
              - Service.config_data
          name: "Configure Service"
          post_run:
            - tendrl.node_agent.atoms.service.validations.check_service_running
          run: tendrl.node_agent.atoms.service.configure.Configure
          type: Update
          uuid: b90a0d97-8c9f-4ab1-8f64-dbb5638159a3
      attrs:
        config_data:
          help: "Configuration data for the service"
          type: String
        config_path:
          help: "configuration file path for the service eg:/etc/tendrl/tendrl.conf"
          type: String
        name:
          help: "Name of the service"
          type: String
        state:
          help: "Service state can be started|stopped|restarted|reloaded"
          type: String
      enabled: true
    Tendrl_context:
      enabled: True
      attrs:
        cluster_id:
          help: "Tendrl managed/generated cluster id for the sds being managed by Tendrl"
          type: String
        sds_name:
          help: "Name of the Tendrl managed sds, eg: 'gluster'"
          type: String
        sds_version:
          help: "Version of the Tendrl managed sds, eg: '3.2.1'"
          type: String
        node_id:
          help: "Tendrl ID for the managed node"
          type: String
    Node_context:
      attrs:
        machine_id:
          help: "Unique /etc/machine-id"
          type: String
        fqdn:
          help: "FQDN of the Tendrl managed node"
          type: String
        node_id:
          help: "Tendrl ID for the managed node"
          type: String
      enabled: true
      value: /nodes/$node.id/node_context
namespace.tendrl.node_agent.gluster_integration:
  flows:
    ImportCluster:
      atoms:
        - tendrl.node_agent.objects.Package.atoms.install
        - tendrl.node_agent.gluster_integration.objects.Config.atoms.generate
        - tendrl.node_agent.objects.File.atoms.write
        - tendrl.node_agent.objects.Node.atoms.cmd
      description: "Import existing Gluster Cluster"
      enabled: true
      inputs:
        mandatory:
          - "Node[]"
          - Tendrl_context.sds_name
          - Tendrl_context.sds_version
          - Tendrl_context.cluster_id
      post_run:
        - tendrl.node_agent.gluster_integration.objects.Tendrl_context.atoms.check_cluster_id_exists
      pre_run:
        - tendrl.node_agent.objects.Node.atoms.check_nodes_up
        - tendrl.node_agent.objects.Tendrl_context.atoms.compare
      run: tendrl.node_agent.gluster_integration.flows.import_cluster.ImportCluster
      type: Create
      uuid: 2f94a48a-05d7-408c-b400-e27827f4edef
      version: 1
  object:
    Config:
      atoms:
        generate:
          enabled: true
          inputs:
            mandatory:
              - Config.etcd_port
              - Config.etcd_connection
          name: "Generate Gluster Integration configuration based on provided inputs"
          outputs:
            - Config.data
            - Config.file_path
          run: tendrl.node_agent.gluster_integration.objects.Config.atoms.generate.Generate
          uuid: 807a1ead-bd70-4f55-99d0-dbd9d76d2a10
      attrs:
        data:
          help: "Configuration data of Gluster Integration for this Tendrl deployment"
          type: String
        etcd_connection:
          help: "Host/IP of the etcd central store for this Tendrl deployment"
          type: String
        etcd_port:
          help: "Port of the etcd central store for this Tendrl deployment"
          type: String
        file_path:
          default: /etc/tendrl/gluster_integration.conf
          help: "Path to the Gluster integration tendrl configuration"
          type: String
      enabled: true
tendrl_schema_version: 0.3
""")
        )

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
                node_uuid=raw_data["node_uuid"],
                fqdn=raw_data["os"]["FQDN"],
            )
        )
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
                    node_uuid=raw_data["node_uuid"],
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
                    node_uuid=raw_data["node_uuid"],
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
                    node_uuid=raw_data["node_uuid"],
                )
            )


def main():
    setup_logging(
        config.get('node_agent', 'log_cfg_path'),
        config.get('node_agent', 'log_level')
    )
    node_id = get_local_node_id()
    machine_id = get_machine_id()

    m = Manager(node_id, machine_id)
    m.start()

    complete = gevent.event.Event()

    def shutdown():
        LOG.info("Signal handler: stopping")
        complete.set()

    gevent.signal(signal.SIGTERM, shutdown)
    gevent.signal(signal.SIGINT, shutdown)

    while not complete.is_set():
        complete.wait(timeout=1)


def get_machine_id():
    cmd = Command({"_raw_params": "cat /etc/machine-id"})
    out, err = cmd.start()
    return out['stdout']


def get_local_node_id():
    # Configure a uuid on the node, so that this can be used by Tendrl for
    # uniquely identifying the node
    try:
        node_agent_key = utils.configure_tendrl_uuid()
        LOG.info("Verified that node uuid exists at"
                 " /etc/tendrl/node_agent_key")

        pull_hardware_inventory.update_node_agent_key(node_agent_key)
    except ValueError as e:
        LOG.error("tendrl node key generation failed: Error: %s" % str(e))
        return
    except Exception:
        LOG.error("Cound not verify/generate valid tendrl node agent id")
        return
    cmd = Command({"_raw_params": "cat %s" % node_agent_key})
    out, err = cmd.start()
    return out['stdout']

if __name__ == "__main__":
    main()
