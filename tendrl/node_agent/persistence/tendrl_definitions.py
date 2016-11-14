from tendrl.common.etcdobj.etcdobj import EtcdObj
from tendrl.common.etcdobj import fields


class TendrlDefinitions(EtcdObj):
    """A table of the Os, lazily updated

    """
    # TODO (rohan) add the definitions in etcd at startup
    __name__ = '/tendrl_definitions_node_agent'

    data = fields.StrField("data")
