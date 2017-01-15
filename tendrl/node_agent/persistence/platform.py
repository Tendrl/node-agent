from tendrl.commons.etcdobj.etcdobj import EtcdObj
from tendrl.commons.etcdobj import fields


class Platform(EtcdObj):
    """A table of the Platform, lazily updated

    """
    __name__ = 'nodes/%s/Platform/'

    node_id = fields.StrField("node_id")
    os = fields.StrField("os")
    os_version = fields.StrField("os_version")
    kernel_version = fields.StrField("kernel_version")

    def render(self):
        self.__name__ = self.__name__ % self.node_id
        return super(Platform, self).render()
