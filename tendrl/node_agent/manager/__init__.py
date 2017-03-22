import logging

import etcd
import gevent
import signal

from tendrl.commons import manager as commons_manager
from tendrl.commons import TendrlNS
from tendrl.integrations import ceph
from tendrl.integrations import gluster
from tendrl import node_agent
from tendrl.node_agent import central_store
from tendrl.node_agent.message.handler import MessageHandler
from tendrl.node_agent import node_sync
from tendrl.node_agent.provisioner.ceph.manager import ProvisioningManager
from tendrl import provisioning


LOG = logging.getLogger(__name__)


class NodeAgentManager(commons_manager.Manager):
    def __init__(self):
        # Initialize the state sync thread which gets the underlying
        # node details and pushes the same to etcd
        super(NodeAgentManager, self).__init__(
            NS.state_sync_thread,
            NS.central_store_thread,
            NS.message_handler_thread
        )

        node_sync.platform_detect.load_and_execute_platform_discovery_plugins()
        node_sync.sds_detect.load_and_execute_sds_discovery_plugins()


def main():
    # NS.node_agent contains the config object,
    # hence initialize it before any other NS
    node_agent.NodeAgentNS()

    # Init NS.tendrl
    TendrlNS()

    # Init NS.provisioning
    provisioning.ProvisioningNS()

    # Init NS.integrations.ceph
    ceph.CephIntegrationNS()

    # Init NS.integrations.gluster
    gluster.GlusterIntegrationNS()

    # Compile all definitions
    NS.compiled_definitions = \
        NS.node_agent.objects.CompiledDefinitions()
    NS.compiled_definitions.merge_definitions([
        NS.tendrl.definitions, NS.node_agent.definitions,
        NS.provisioning.definitions,
        NS.integrations.ceph.definitions,
        NS.integrations.gluster.definitions
    ])
    NS.node_agent.compiled_definitions = NS.compiled_definitions

    # Every process needs to set a NS.type
    # Allowed types are "node", "integration", "monitoring"
    NS.type = "node"

    NS.central_store_thread = central_store.NodeAgentEtcdCentralStore()
    NS.first_node_inventory_sync = True
    NS.state_sync_thread = node_sync.NodeAgentSyncThread()
    # TODO(team) the prov plugin to read from a config file
    NS.provisioner = ProvisioningManager("CephInstallerPlugin")

    NS.compiled_definitions.save()
    NS.node_context.save()
    
    # Check if Node is part of any Tendrl imported/created sds cluster
    try:
        NS.tendrl_context = NS.tendrl_context.load()
        LOG.info("Node %s is part of sds cluster %s",
                 NS.node_context.node_id,
                 NS.tendrl_context.integration_id)
    except etcd.EtcdKeyNotFound:
        LOG.info("Node %s is not part of any sds cluster",
                 NS.node_context.node_id)
        pass
    NS.tendrl_context.save()
    NS.node_agent.definitions.save()
    NS.node_agent.config.save()
    NS.message_handler_thread = MessageHandler()

    NS.publisher_id = "node_agent"

    m = NodeAgentManager()
    m.start()

    complete = gevent.event.Event()

    def shutdown():
        LOG.info("Signal handler: stopping")
        complete.set()
        m.stop()

    gevent.signal(signal.SIGTERM, shutdown)
    gevent.signal(signal.SIGINT, shutdown)

    while not complete.is_set():
        complete.wait(timeout=1)


if __name__ == "__main__":
    main()
