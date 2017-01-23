from tendrl.commons.etcdobj import EtcdObj
from tendrl.node_agent import objects


class Platform(objects.NodeAgentBaseObject):
    def __init__(self, os=None, os_version=None,
                 kernel_version=None,
                 *args, **kwargs):
        super(Platform, self).__init__(*args, **kwargs)
        self.value = 'nodes/%s/Platform'
        self.kernel_version = kernel_version
        self.os = os
        self.os_version = os_version
        self._etcd_cls = _PlatformEtcd


class _PlatformEtcd(EtcdObj):
    """A table of the platform, lazily updated

    """
    __name__ = 'nodes/%s/Platform'
    _tendrl_cls = Platform

    def render(self):
        self.__name__ = self.__name__ % tendrl_ns.node_context.node_id
        return super(_PlatformEtcd, self).render()
