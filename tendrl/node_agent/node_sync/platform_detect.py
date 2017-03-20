import logging

import etcd

from tendrl.node_agent.discovery.platform import manager as platform_manager

LOG = logging.getLogger(__name__)


def load_and_execute_platform_discovery_plugins():
    # platform plugins
    LOG.info("load_and_execute_platform_discovery_plugins, platform \
     plugins")
    try:
        pMgr = platform_manager.PlatformManager()
    except ValueError as ex:
        LOG.error(
            'Failed to init PlatformManager. \Error %s', str(ex))
        return
    # execute the platform plugins
    for plugin in pMgr.get_available_plugins():
        platform_details = plugin.discover_platform()
        if len(platform_details.keys()) > 0:
            # update etcd
            try:
                NS.platform = NS.tendrl.objects.Platform(
                    os=platform_details["Name"],
                    os_version=platform_details["OSVersion"],
                    kernel_version=platform_details["KernelVersion"],
                )
                NS.platform.save()

            except etcd.EtcdException as ex:
                LOG.error(
                    'Failed to update etcd . \Error %s', str(ex))
            break
