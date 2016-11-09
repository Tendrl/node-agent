from tendrl.bridge_common.etcdobj.etcdobj import EtcdObj
from tendrl.bridge_common.etcdobj import fields


class Memory(EtcdObj):
    """A table of the memory, lazily updated

    """
    __name__ = 'nodes/%s/memory'

    node_uuid = fields.StrField("node_uuid")
    total_size = fields.StrField("total_size")
    total_swap = fields.StrField("total_swap")

    def render(self):
        self.__name__ = self.__name__ % self.node_uuid
        return super(Memory, self).render()
