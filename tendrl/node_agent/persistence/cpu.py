from tendrl.bridge_common.etcdobj.etcdobj import EtcdObj
from tendrl.bridge_common.etcdobj import fields


class Cpu(EtcdObj):
    """A table of the cpu, lazily updated

    """
    __name__ = 'nodes/%s/cpu'

    node_uuid = fields.StrField("node_uuid")
    model = fields.StrField("model")
    vendor_id = fields.StrField("vendor_id")
    model_name = fields.StrField("model_name")
    architecture = fields.StrField("architecture")
    cores_per_socket = fields.StrField("cores_per_socket")
    cpu_op_mode = fields.StrField("cpu_op_mode")
    cpu_family = fields.StrField("cpu_family")
    cpu_count = fields.StrField("cpu_count")

    def render(self):
        self.__name__ = self.__name__ % self.node_uuid
        return super(Cpu, self).render()
