from tendrl.commons.etcdobj.etcdobj import EtcdObj
from tendrl.commons.etcdobj import fields


class TendrlContext(EtcdObj):
    """A table of the tendrl context, lazily updated

    """
    __name__ = 'nodes/%s/Tendrl_context/'

    node_id = fields.StrField("node_id")
    sds_version = fields.StrField("sds_version")
    sds_name = fields.StrField("sds_name")
    cluster_id = fields.StrField("cluster_id")

    def render(self):
        self.__name__ = self.__name__ % self.node_id
        return super(TendrlContext, self).render()
