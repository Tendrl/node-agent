from tendrl.bridge_common.etcdobj.etcdobj import EtcdObj
from tendrl.bridge_common.etcdobj import fields


class NodeMetadata(EtcdObj):
    """A table of the node metadata, lazily updated

    """
    __name__ = 'nodes/metadata/%s'

    node_uuid = fields.StrField("node_uuid")
    node_machine_uuid = fields.StrField("node_machine_uuid")
    fqdn = fields.StrField("fqdn")

    def render(self):
        self.__name__ = self.__name__ % self.node_uuid
        return super(NodeMetadata, self).render()
