import etcd


def run():
    try:
        nodes = NS._int.client.read("/nodes")
    except etcd.EtcdKeyNotFound:
        return

    for node in nodes.leaves:
        node_id = node.key.split('/')[-1]
        _node_context = NS.tendrl.objects.NodeContext(
            node_id=node_id
        ).load()
        _node_context.watch_attrs()
    return
