import etcd

from tendrl.commons.utils import etcd_utils


def run():
    try:
        nodes = etcd_utils.read("/nodes")
        for node in nodes.leaves:
            node_id = node.key.split("/")[-1]
            _node_context = NS.tendrl.objects.NodeContext(
                node_id=node_id
            ).load()
            if _node_context.fqdn:
                _node_context.watch_attrs()
    except etcd.EtcdKeyNotFound:
        pass
    return
