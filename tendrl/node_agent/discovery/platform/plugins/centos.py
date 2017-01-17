import logging
import platform
from tendrl.node_agent.discovery.platform import base


LOG = logging.getLogger(__name__)


class CentosPlugin(base.PlatformDiscoverPlugin):

    def discover_platform(self):
        os_out = platform.linux_distribution()

        osinfo = {
            'Name': os_out[0],
            'OSVersion': os_out[1],
            'KernelVersion': platform.release()
        }
        return osinfo
