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
    cluster_id = fields.StrField("cluster_id")
    sds_pkg_name = fields.StrField("sds_pkg_name")
    sds_pkg_version = fields.StrField("sds_pkg_version")
    detected_cluster_id = fields.StrField("detected_cluster_id")
    cluster_attrs = fields.DictField("cluster_attrs", {'str': 'str'})

    def render(self):
        self.__name__ = self.__name__ % self.node_id
        return super(NodeContext, self).render()
