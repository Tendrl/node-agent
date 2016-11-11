from tendrl.bridge_common.etcdobj.etcdobj import EtcdObj
from tendrl.bridge_common.etcdobj import fields


class TendrlDefinitions(EtcdObj):
    """A table of the Os, lazily updated

    """
    __name__ = '/tendrl_definitions_node_agent'

    data = fields.StrField("data")
