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


class Memory(EtcdObj):
    """A table of the memory, lazily updated

    """
    __name__ = 'nodes/%s/memory'

    node_uuid = fields.StrField("node_uuid")
    total_size = fields.StrField("total_size")
    total_swap = fields.StrField("total_swap")

    def render(self):
        self.__name__ = self.__name__ % self.node_uuid
        return super(Memory, self).render()


class Os(EtcdObj):
    """A table of the Os, lazily updated

    """
    __name__ = 'nodes/%s/os'

    node_uuid = fields.StrField("node_uuid")
    os = fields.StrField("os")
    os_version = fields.StrField("os_version")
    kernel_version = fields.StrField("kernel_version")
    selinux_mode = fields.StrField("selinux_mode")

    def render(self):
        self.__name__ = self.__name__ % self.node_uuid
        return super(Os, self).render()
