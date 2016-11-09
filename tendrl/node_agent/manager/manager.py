import logging
import signal

import gevent.event
import gevent.greenlet
import json
import pull_hardware_inventory
from rpc import EtcdThread
from tendrl.node_agent import log

from tendrl.node_agent.persistence.persister import Persister
from tendrl.node_agent.persistence.servers import Cpu
from tendrl.node_agent.persistence.servers import Memory
from tendrl.node_agent.persistence.servers import NodeMetadata
from tendrl.node_agent.persistence.servers import Os
import time
import uuid

LOG = logging.getLogger(__name__)
HARDWARE_INVENTORY_FILE = "/etc/tendrl/tendrl-node-inventory.json"
TENDRL_NODE_ID_FILE = "/etc/tendrl/node_agent_key"


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

    def __init__(self):
        self._complete = gevent.event.Event()

        self._user_request_thread = EtcdThread(self)
        self._discovery_thread = TopLevelEvents(self)
        self.persister = Persister()

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

    def on_pull(self, raw_data):
        LOG.info("on_pull, Updating node metadata data")
        self.persister.update_node_metadata(
            NodeMetadata(
                updated=str(time.time()),
                node_machine_uuid=raw_data["node_machine_uuid"],
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


def configure_tendrl_uuid():
    # check if valid uuid is already present in tendrl_node_id_file.
    # if not present generate one and update the file
    try:
        with open(TENDRL_NODE_ID_FILE) as f:
            node_id = f.read()
            uuid.UUID(node_id, version=4)
            LOG.info("tendrl node uuid already exists")
            return
    except ValueError:
        with open(TENDRL_NODE_ID_FILE, 'w') as f:
            f.write(str(uuid.uuid4()))
        LOG.info("tendrl node uuid is being generated")
        return
    except IOError:
        with open(TENDRL_NODE_ID_FILE, 'w') as f:
            f.write(str(uuid.uuid4()))
        LOG.info("tendrl node uuid is being generated")
        return


def main():
    log.setup_logging()
    # Configure a uuid on the node, so that this can be used by Tendrl for
    # uniquely identifying the node
    try:
        configure_tendrl_uuid()
        LOG.info("Verified that node uuid exists at"
                 " /etc/tendrl/node_agent_key")
    except Exception:
        LOG.error("Cound not verify/generate valid tendrl node agent id")
        return

    m = Manager()
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
