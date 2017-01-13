from abc import abstractmethod
import six
from tendrl.node_agent.discovery.plugin import PluginMount


@six.add_metaclass(PluginMount)
class PlatformDiscoverPlugin(object):

    @abstractmethod
    def discover_platform(self):
        raise NotImplementedError()
