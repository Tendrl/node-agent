from tendrl.commons.etcdobj.etcdobj import EtcdObj
from tendrl.commons.etcdobj import fields


class Os(EtcdObj):
    """A table of the Os, lazily updated

    """
    __name__ = 'nodes/%s/Os/'

    node_id = fields.StrField("node_id")
    os = fields.StrField("os")
    os_version = fields.StrField("os_version")
    kernel_version = fields.StrField("kernel_version")
    selinux_mode = fields.StrField("selinux_mode")

    def render(self):
        self.__name__ = self.__name__ % self.node_id
        return super(Os, self).render()
