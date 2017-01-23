import platform
import socket
from tendrl.commons.utils import cmd_utils
from tendrl.commons.etcdobj import EtcdObj
from tendrl.node_agent import objects


class Os(objects.NodeAgentBaseObject):
    def __init__(self, kernel_version=None, os=None,
                 os_version=None, selinux_mode=None,
                 *args, **kwargs):
        super(Os, self).__init__(*args, **kwargs)
        os_details = self._getNodeOs()
        self.value = 'nodes/%s/Os'
        self.kernel_version = kernel_version or os_details["KernelVersoion"]
        self.os = os or os_details["Name"]
        self.os_version = os_version or os_details["OSVersion"]
        self.selinux_mode = selinux_mode or os_details["SELinuxMode"]
        self._etcd_cls = _OsEtcd

    def _getNodeOs(self):
        cmd = cmd_utils.Command("getenforce")
        out, err, rc = cmd.run(tendrl_ns.config.data[
                                   'tendrl_ansible_exec_file'])
        se_out = out['stdout']

        os_out = platform.linux_distribution()

        osinfo = {
            'Name': os_out[0],
            'OSVersion': os_out[1],
            'KernelVersion': platform.release(),
            'SELinuxMode': se_out,
            'FQDN': socket.getfqdn()
        }

        return osinfo


class _OsEtcd(EtcdObj):
    """A table of the OS, lazily updated

    """
    __name__ = 'nodes/%s/Os'
    _tendrl_cls = Os

    def render(self):
        self.__name__ = self.__name__ % tendrl_ns.node_context.node_id
        return super(_OsEtcd, self).render()
