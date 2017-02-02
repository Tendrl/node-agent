import logging

import etcd
import gevent
import signal
from tendrl.commons import manager as commons_manager

from tendrl.node_agent import node_sync
from tendrl.node_agent import central_store
from tendrl.node_agent.discovery.platform.manager import PlatformManager
from tendrl.node_agent.discovery.sds.manager import SDSDiscoveryManager

LOG = logging.getLogger(__name__)


class NodeAgentManager(commons_manager.Manager):
    def __init__(self):
        # Initialize the state sync thread which gets the underlying
        # node details and pushes the same to etcd
        super(NodeAgentManager, self).__init__(
            tendrl_ns.state_sync_thread,
            tendrl_ns.central_store_thread
        )

        self.load_and_execute_platform_discovery_plugins()
        self.load_and_execute_sds_discovery_plugins()

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
                    tendrl_ns.platform = tendrl_ns.node_agent.objects.Platform(
                        os=platform_details["Name"],
                        os_version=platform_details["OSVersion"],
                        kernel_version=platform_details["KernelVersion"],
                        )
                    tendrl_ns.platform.save()

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
            if sds_details:
                try:
                    tendrl_ns.node_agent.objects.DetectedCluster(
                        detected_cluster_id=sds_details['detected_cluster_id'],
                        sds_pkg_name=sds_details['pkg_name'],
                        sds_pkg_version=sds_details['pkg_version'],
                    ).save()
                except etcd.EtcdException as ex:
                    LOG.error('Failed to update etcd . \Error %s' % str(ex))
                break


def main():
    tendrl_ns.central_store_thread = central_store.NodeAgentEtcdCentralStore()
    tendrl_ns.state_sync_thread = node_sync.NodeAgentSyncThread()

    tendrl_ns.node_context.save()
    tendrl_ns.tendrl_context.save()
    tendrl_ns.definitions.save()
    tendrl_ns.config.save()

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
