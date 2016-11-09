from tendrl.bridge_common.etcdobj.etcdobj import EtcdObj
from tendrl.bridge_common.etcdobj import fields


class Fqdn(EtcdObj):
    """A table of the Os, lazily updated

    """
    __name__ = 'nodes/%s/fqdn'

    node_uuid = fields.StrField("node_uuid")
    fqdn = fields.StrField("fqdn")

    def render(self):
        self.__name__ = self.__name__ % self.node_uuid
        return super(Fqdn, self).render()
