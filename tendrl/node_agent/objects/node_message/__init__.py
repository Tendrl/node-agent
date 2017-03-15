from tendrl.commons import etcdobj
from tendrl.commons.message import Message as message
from tendrl.commons import objects


class NodeMessage(message, objects.BaseObject):
    def __init__(self, **node_message):
        super(NodeMessage, self).__init__(**node_message)

        self.value = 'nodes/%s/Messages/%s'
        self._etcd_cls = _NodeMessageEtcd

    def load_definition(self):
        return {}


class _NodeMessageEtcd(etcdobj.EtcdObj):
    """Node message object, lazily updated

    """
    __name__ = 'nodes/%s/Messages/%s'
    _tendrl_cls = NodeMessage

    def render(self):
        self.__name__ = self.__name__ % (
            self.node_id, self.message_id
        )
        return super(_NodeMessageEtcd, self).render()
