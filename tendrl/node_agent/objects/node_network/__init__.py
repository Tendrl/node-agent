from tendrl.commons.etcdobj import EtcdObj
from tendrl.commons import objects


class NodeNetwork(objects.BaseObject):

    def __init__(self, interface=None, interface_id=None,
                 ipv4=None, ipv6=None, netmask=None, subnet=None,
                 status=None, sysfs_id=None, device_link=None,
                 interface_type=None, model=None, driver_modules=None,
                 driver=None, drive=None, hw_address=None, link_detected=None,
                 *args, **kwargs):
        super(NodeNetwork, self).__init__(*args, **kwargs)
        self.value = 'nodes/%s/Networks/%s'
        self.interface = interface
        self.interface_id = interface_id
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.netmask = netmask
        self.subnet = subnet
        self.status = status
        self.sysfs_id = sysfs_id
        self.device_link = device_link
        self.drive = drive
        self.interface_type = interface_type
        self.model = model
        self.driver_modules = driver_modules
        self.driver = driver
        self.hw_address = hw_address
        self.link_detected = link_detected
        self._etcd_cls = _NodeNetworkEtcd

    def load_definition(self):
        return {}


class _NodeNetworkEtcd(EtcdObj):
    """A table of the Node Network, lazily updated

    """
    __name__ = 'nodes/%s/Networks/%s'
    _tendrl_cls = NodeNetwork

    def render(self):
        self.__name__ = self.__name__ % (
            NS.node_context.node_id, self.interface
        )
        return super(_NodeNetworkEtcd, self).render()
