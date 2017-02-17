from tendrl.commons import etcdobj

from tendrl.node_agent import objects


class Node(objects.NodeAgentBaseObject):
    def __init__(self, fqdn=None,
                 status=None, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self.value = 'nodes/%s'
        self.list = 'nodes/'
        self.fqdn = fqdn
        self.status = status
        self._etcd_cls = _NodeEtcd


class _NodeEtcd(etcdobj.EtcdObj):
    """A table of the node, lazily updated

    """
    __name__ = 'nodes/%s'
    _tendrl_cls = Node

    def render(self):
        self.__name__ = self.__name__ % tendrl_ns.node_context.node_id
        return super(_NodeEtcd, self).render()
