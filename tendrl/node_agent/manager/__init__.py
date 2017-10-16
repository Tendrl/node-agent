import signal
import threading

from etcd import EtcdKeyNotFound
from etcd import EtcdException

from tendrl.commons.event import Event
from tendrl.commons import manager as commons_manager
from tendrl.commons.message import Message
from tendrl.commons.objects.node_alert_counters import NodeAlertCounters
from tendrl.commons import TendrlNS
from tendrl.commons.utils import etcd_utils
from tendrl.node_agent.provisioner.ceph.manager import \
    ProvisioningManager as CephProvisioningManager
from tendrl.node_agent.provisioner.gluster.manager import \
    ProvisioningManager as GlusterProvisioningManager

from tendrl import node_agent
from tendrl.node_agent.message.handler import MessageHandler
from tendrl.node_agent import node_sync

from tendrl.integrations.ceph import sds_sync as \
    ceph_integrations_sds_sync

from tendrl.integrations.gluster import GlusterIntegrationNS


class NodeAgentManager(commons_manager.Manager):
    def __init__(self):
        # Initialize the state sync thread which gets the underlying
        # node details and pushes the same to etcd
        super(NodeAgentManager, self).__init__(
            NS.state_sync_thread,
            message_handler_thread=NS.message_handler_thread
        )

        node_sync.platform_detect.sync()
        node_sync.sds_detect.sync()


def main():
    # NS.node_agent contains the config object,
    # hence initialize it before any other NS
    node_agent.NodeAgentNS()
    # Init NS.tendrl
    TendrlNS()

    # Init NS.provisioning
    # TODO(team) remove NS.provisioner and use NS.provisioning.{ceph, gluster}
    # provisioning.ProvisioningNS()

    # Init NS.integrations.ceph
    # TODO(team) add all short circuited ceph(import/create) NS.tendrl.flows
    #  to NS.integrations.ceph
    # ceph.CephIntegrationNS()

    # Init NS.integrations.gluster
    # TODO(team) add all short circuited ceph(import/create) NS.tendrl.flows
    #  to NS.integrations.ceph
    GlusterIntegrationNS()

    # Compile all definitions
    NS.compiled_definitions = \
        NS.node_agent.objects.CompiledDefinitions()
    NS.compiled_definitions.merge_definitions([
        NS.tendrl.definitions, NS.node_agent.definitions,
        NS.integrations.gluster.definitions])
    NS.node_agent.compiled_definitions = NS.compiled_definitions

    # Every process needs to set a NS.type
    # Allowed types are "node", "integration", "monitoring"
    NS.type = "node"

    NS.first_node_inventory_sync = True
    NS.state_sync_thread = node_sync.NodeAgentSyncThread()

    NS.compiled_definitions.save()
    NS.node_context.save()

    NS.tendrl_context.save()
    NS.node_agent.definitions.save()
    # NS.integrations.ceph.definitions.save()
    NS.node_agent.config.save()
    NS.publisher_id = "node_agent"
    NS.message_handler_thread = MessageHandler()

    NS.ceph_provisioner = CephProvisioningManager(
        NS.tendrl.definitions.get_parsed_defs()["namespace.tendrl"][
            'ceph_provisioner']
    )
    NS.gluster_provisioner = GlusterProvisioningManager(
        NS.tendrl.definitions.get_parsed_defs()["namespace.tendrl"][
            'gluster_provisioner']
    )
    if NS.config.data.get("with_internal_profiling", False):
        from tendrl.commons import profiler
        profiler.start()
    # Initialize alert count
    try:
        key = '/nodes/%s/alert_counters' % NS.node_context.node_id
        etcd_utils.read(key)
    except(EtcdException)as ex:
        if type(ex) == EtcdKeyNotFound:
            NodeAlertCounters(node_id=NS.node_context.node_id).save()   
    m = NodeAgentManager()
    m.start()

    if NS.tendrl_context.sds_name == "ceph" and \
        NS.tendrl_context.integration_id:
        NS.ceph_integrations_sync_thread = \
            ceph_integrations_sds_sync.CephIntegrtaionsSyncThread()
        NS.ceph_integrations_sync_thread.start()

    complete = threading.Event()

    def shutdown(signum, frame):
        Event(
            Message(
                priority="debug",
                publisher=NS.publisher_id,
                payload={"message": "Signal handler: stopping"}
            )
        )
        complete.set()
        m.stop()
        if NS.tendrl_context.sds_name == "ceph" and \
            NS.tendrl_context.integration_id:
            NS.ceph_integrations_sync_thread.stop()

    def reload_config(signum, frame):
        Event(
            Message(
                priority="debug",
                publisher=NS.publisher_id,
                payload={"message": "Signal handler: SIGHUP"}
            )
        )
        NS.config = NS.config.__class__()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGHUP, reload_config)

    while not complete.is_set():
        complete.wait(timeout=1)


if __name__ == "__main__":
    main()
