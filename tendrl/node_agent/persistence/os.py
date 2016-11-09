from tendrl.bridge_common.etcdobj.etcdobj import EtcdObj
from tendrl.bridge_common.etcdobj import fields


class Os(EtcdObj):
    """A table of the Os, lazily updated

    """
    __name__ = 'nodes/%s/os'

    node_uuid = fields.StrField("node_uuid")
    os = fields.StrField("os")
    os_version = fields.StrField("os_version")
    kernel_version = fields.StrField("kernel_version")
    selinux_mode = fields.StrField("selinux_mode")

    def render(self):
        self.__name__ = self.__name__ % self.node_uuid
        return super(Os, self).render()
