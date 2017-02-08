from tendrl.commons.etcdobj import EtcdObj
from tendrl.node_agent import objects


class File(objects.NodeAgentBaseObject):
    def __init__(self, data=None, file_path=None,
                 *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.data = data
        self.file_path = file_path
        self._etcd_cls = _FileEtcd


class _FileEtcd(EtcdObj):
    """A table of the file, lazily updated

    """
    __name__ = 'nodes/%s/File'
    _tendrl_cls = File

    def render(self):
        self.__name__ = self.__name__ % (
            tendrl_ns.node_context.node_id
        )
        return super(_FileEtcd, self).render()
