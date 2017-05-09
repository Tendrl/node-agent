from abc import abstractmethod
import six


class PluginMount(type):

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.register_plugin(cls)

    def register_plugin(cls, plugin):
        instance = plugin()
        cls.plugins.append(instance)


@six.add_metaclass(PluginMount)
class ProvisionerBasePlugin(object):

    @abstractmethod
    def setup_gluster_node(self, hosts, packages, repo):
        raise NotImplementedError()

    @abstractmethod
    def create_gluster_cluster(self, hosts):
        raise NotImplementedError()

    @abstractmethod
    def setup(self):
        raise NotImplementedError()

    @abstractmethod
    def expand_gluster_cluster(self, hosts):
        raise NotImplementedError()

    @abstractmethod
    def shrink_gluster_cluster(self, hosts):
        raise NotImplementedError()
