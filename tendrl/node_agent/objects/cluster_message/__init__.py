from tendrl.commons import etcdobj
from tendrl.commons.message import Message as message
from tendrl.commons import objects


class ClusterMessage(objects.BaseObject, message):
    internal = True
    def __init__(self, **cluster_message):
        self._defs = {}
        message.__init__(self, **cluster_message)
        objects.BaseObject.__init__(self)
        
        self.value = 'clusters/%s/messages/%s'
        self._etcd_cls = _ClusterMessageEtcd

    def save(self):
        super(ClusterMessage, self).save(update=False)

class _ClusterMessageEtcd(etcdobj.EtcdObj):
    """Cluster message object, lazily updated

    """
    __name__ = 'clusters/%s/messages/%s'
    _tendrl_cls = ClusterMessage

    def render(self):
        self.__name__ = self.__name__ % (
            self.cluster_id, self.message_id
        )
        return super(_ClusterMessageEtcd, self).render()
