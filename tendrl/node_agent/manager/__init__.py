import etcd
import gevent
import signal
import sys

from tendrl.commons import manager as commons_manager
from tendrl.commons import TendrlNS
from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.node_agent.provisioner.ceph.manager import \
    ProvisioningManager as CephProvisioningManager
from tendrl.node_agent.provisioner.gluster.manager import \
    ProvisioningManager as GlusterProvisioningManager

from tendrl.integrations import ceph
from tendrl.integrations import gluster
from tendrl import node_agent
from tendrl.node_agent.message.handler import MessageHandler
from tendrl.node_agent import node_sync
from tendrl import provisioning


class NodeAgentManager(commons_manager.Manager):
    def __init__(self):
        # Initialize the state sync thread which gets the underlying
        # node details and pushes the same to etcd
        super(NodeAgentManager, self).__init__(
            NS.state_sync_thread,
            message_handler_thread=NS.message_handler_thread
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
    # TODO(team) remove NS.provisioner and use NS.provisioning.{ceph, gluster}
    #provisioning.ProvisioningNS()

    # Init NS.integrations.ceph
    # TODO(team) add all short circuited ceph(import/create) NS.tendrl.flows to NS.integrations.ceph
    #ceph.CephIntegrationNS()

    # Init NS.integrations.gluster
    # TODO(team) add all short circuited ceph(import/create) NS.tendrl.flows to NS.integrations.ceph
    #gluster.GlusterIntegrationNS()

    # Compile all definitions
    NS.compiled_definitions = \
        NS.node_agent.objects.CompiledDefinitions()
    NS.compiled_definitions.merge_definitions([
        NS.tendrl.definitions, NS.node_agent.definitions])
    NS.node_agent.compiled_definitions = NS.compiled_definitions

    # Every process needs to set a NS.type
    # Allowed types are "node", "integration", "monitoring"
    NS.type = "node"

    NS.first_node_inventory_sync = True
    NS.state_sync_thread = node_sync.NodeAgentSyncThread()

    NS.compiled_definitions.save()
    NS.node_context.save()

    # Check if Node is part of any Tendrl imported/created sds cluster
    try:
        NS.tendrl_context = NS.tendrl_context.load()
        sys.stdout.write("Node %s is part of sds cluster %s" % (
            NS.node_context.node_id, NS.tendrl_context.integration_id))
    except etcd.EtcdKeyNotFound:
        sys.stdout.write("Node %s is not part of any sds cluster" %
                         NS.node_context.node_id)
        pass
    NS.tendrl_context.save()
    NS.node_agent.definitions.save()
    NS.node_agent.config.save()
    NS.publisher_id = "node_agent"
    NS.message_handler_thread = MessageHandler()

    NS.ceph_provisioner = CephProvisioningManager(
        NS.tendrl.definitions.get_parsed_defs()["namespace.tendrl"]['ceph_provisioner']
    )
    NS.gluster_provisioner = GlusterProvisioningManager(
        NS.tendrl.definitions.get_parsed_defs()["namespace.tendrl"]['gluster_provisioner']
    )

    m = NodeAgentManager()
    m.start()

    complete = gevent.event.Event()

    def shutdown():
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "Signal handler: stopping"}
            )
        )
        complete.set()
        m.stop()
    
    def reload_config():
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "Signal handler: SIGHUP"}
            )
        )
        NS.config = NS.config.__class__()

    gevent.signal(signal.SIGTERM, shutdown)
    gevent.signal(signal.SIGINT, shutdown)
    gevent.signal(signal.SIGHUP, reload_config)

    while not complete.is_set():
        complete.wait(timeout=1)


if __name__ == "__main__":
    main()
