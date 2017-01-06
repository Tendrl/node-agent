from tendrl.commons.etcdobj.etcdobj import EtcdObj
from tendrl.commons.etcdobj import fields


class TendrlDefinitions(EtcdObj):
    """A table of the Os, lazily updated

    """
    # TODO(rohan) add the definitions in etcd at startup
    __name__ = '/tendrl_definitions_node-agent'

    data = fields.StrField("data")
