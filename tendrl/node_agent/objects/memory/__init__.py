from tendrl.commons.utils import cmd_utils
from tendrl.commons.etcdobj import EtcdObj

from tendrl.node_agent import objects


class Memory(objects.NodeAgentBaseObject):
    def __init__(self, total_size=None, swap_total=None,
                 *args, **kwargs):
        super(Memory, self).__init__(*args, **kwargs)
        memory = self._getNodeMemory()
        self.value = 'nodes/%s/Memory'
        self.total_size = total_size or memory["TotalSize"]
        self.swap_total = swap_total or memory["SwapTotal"]
        self._etcd_cls = _MemoryEtcd

    def _getNodeMemory(self):
        '''returns structure

        {"nodename": [{"TotalSize": "totalsize",

                   "SwapTotal": "swaptotal",

                   "Type":      "type"}, ...], ...}

        '''

        cmd = cmd_utils.Command("cat /proc/meminfo")
        out, err, rc = cmd.run(tendrl_ns.config.data[
                                   'tendrl_ansible_exec_file'])
        out = out['stdout']

        if out:
            info_list = out.split('\n')
            memoinfo = {
                'TotalSize': info_list[0].split(':')[1].strip(),
                'SwapTotal': info_list[14].split(':')[1].strip()
            }
        else:
            memoinfo = {
                'TotalSize': '',
                'SwapTotal': ''
            }

        return memoinfo


class _MemoryEtcd(EtcdObj):
    """A table of the memory, lazily updated

    """
    __name__ = 'nodes/%s/Memory'
    _tendrl_cls = Memory

    def render(self):
        self.__name__ = self.__name__ % tendrl_ns.node_context.node_id
        return super(_MemoryEtcd, self).render()
