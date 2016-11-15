from tendrl.common.etcdobj.etcdobj import EtcdObj
from tendrl.common.etcdobj import fields


class Node(EtcdObj):
    """A table of the Os, lazily updated

    """
    __name__ = 'nodes/%s/Node'

    node_id = fields.StrField("node_id")
    fqdn = fields.StrField("fqdn")
    status = fields.StrField("status")

    def render(self):
        self.__name__ = self.__name__ % self.node_id
        return super(Node, self).render()
