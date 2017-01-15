import abc
import six

from tendrl.node_agent.discovery.plugin import PluginMount
from tendrl.node_agent.discovery.sds.exceptions \
    import DiscoverSDSPluginNotImplementedError


@six.add_metaclass(PluginMount)
class DiscoverSDSPlugin(object):
    @abc.abstractmethod
    def discover_storage_system(self):
        raise DiscoverSDSPluginNotImplementedError(
            'define the function discover_storage_system to use this class'
        )
