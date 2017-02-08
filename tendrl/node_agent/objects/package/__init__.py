from tendrl.commons.etcdobj import EtcdObj
from tendrl.node_agent import objects


class Package(objects.NodeAgentBaseObject):
    def __init__(self, name=None, pkg_type=None,
                 state=None, version=None,
                 *args, **kwargs):
        super(Package, self).__init__(*args, **kwargs)
        self.name = name
        self.pkg_type = pkg_type
        self.state = state
        self.version = version
        self._etcd_cls = _PackageEtcd


class _PackageEtcd(EtcdObj):
    """A table of the node, lazily updated

    """
    __name__ = 'nodes/%s/Package/%s'
    _tendrl_cls = Package

    def render(self):
        self.__name__ = self.__name__ % (
            tendrl_ns.node_context.node_id,
            self.name
        )
        return super(_PackageEtcd, self).render()
