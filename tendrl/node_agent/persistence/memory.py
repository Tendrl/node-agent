from tendrl.common.etcdobj.etcdobj import EtcdObj
from tendrl.common.etcdobj import fields


class Memory(EtcdObj):
    """A table of the memory, lazily updated

    """
    __name__ = 'nodes/%s/Memory'

    node_id = fields.StrField("node_id")
    total_size = fields.StrField("total_size")
    total_swap = fields.StrField("total_swap")

    def render(self):
        self.__name__ = self.__name__ % self.node_id
        return super(Memory, self).render()
