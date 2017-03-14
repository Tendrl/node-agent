from tendrl.commons import etcdobj
from tendrl.commons.message import Message as message
from tendrl.commons import objects


class ClusterMessage(message, objects.BaseObject):
    def __init__(self, **cluster_message):
        super(ClusterMessage, self).__init__(**cluster_message)

        self.value = 'clusters/%s/Messages/%s'
        self._etcd_cls = _ClusterMessageEtcd


class _ClusterMessageEtcd(etcdobj.EtcdObj):
    """Cluster message object, lazily updated

    """
    __name__ = 'clusters/%s/Messages/%s'
    _tendrl_cls = ClusterMessage

    def render(self):
        self.__name__ = self.__name__ % (
            self.cluster_id, self.message_id
        )
        return super(_ClusterMessageEtcd, self).render()
