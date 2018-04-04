def run():
    nodes = NS.tendrl.objects.Node().load_all()
    if nodes is None:
        return

    for node in nodes:
        _node_context = NS.tendrl.objects.NodeContext(
            node_id=node.node_id
        ).load()
        _node_context.watch_attrs()
    return
