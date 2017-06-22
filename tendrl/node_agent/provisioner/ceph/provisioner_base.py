from abc import abstractmethod
import six


class PluginMount(type):

    def __init__(cls, *args, **kwargs):
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
    def install_mon(self, mons):
        raise NotImplementedError()

    @abstractmethod
    def install_osd(self, osds):
        raise NotImplementedError()

    @abstractmethod
    def configure_mon(
        self,
        host,
        cluster_id,
        cluster_name,
        ip_address,
        cluster_network,
        public_network,
        monitors,
        mon_secret=None
    ):
        raise NotImplementedError()

    @abstractmethod
    def configure_osd(
        self,
        host,
        devices,
        cluster_id,
        cluster_name,
        journal_size,
        cluster_network,
        public_network,
        monitors
    ):
        raise NotImplementedError()

    @abstractmethod
    def task_status(self, task_id):
        raise NotImplementedError()

    @abstractmethod
    def setup(self):
        raise NotImplementedError()
