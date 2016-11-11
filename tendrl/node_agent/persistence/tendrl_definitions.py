from tendrl.bridge_common.etcdobj.etcdobj import EtcdObj
from tendrl.bridge_common.etcdobj import fields


class TendrlDefinitions(EtcdObj):
    """A table of the Os, lazily updated

    """
    __name__ = '/tendrl_definitions_node_agent'

    data = fields.StrField("data")

    def render(self):
        self.__name__ = self.__name__ % self.node_uuid
        return super(TendrlDefinitions, self).render()
