from tendrl.commons.etcdobj.etcdobj import EtcdObj
from tendrl.commons.etcdobj import fields


class NodeContext(EtcdObj):
    """A table of the node context, lazily updated

    """
    __name__ = 'nodes/%s/Node_context'

    node_id = fields.StrField("node_id")
    machine_id = fields.StrField("machine_id")
    fqdn = fields.StrField("fqdn")
    tags = fields.StrField("tags")

    def render(self):
        self.__name__ = self.__name__ % self.node_id
        return super(NodeContext, self).render()
