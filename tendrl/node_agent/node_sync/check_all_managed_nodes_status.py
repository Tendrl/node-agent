import etcd


def run():
    try:
        nodes = NS._int.client.read("/nodes")
    except etcd.EtcdKeyNotFound:
        return
    
    for node in nodes.leaves:
        node_id = node.key.split('/')[-1]
        try:
            NS._int.client.write(
                "/nodes/{0}/NodeContext/status".format(node_id),
                "DOWN",
                prevExist=False
            )            
        except etcd.EtcdAlreadyExist:
            pass
        try:
            _tc = NS.tendrl.objects.TendrlContext(node_id=node_id).load()
            if _tc.integration_id:
                NS._int.client.write(
                    "/clusters/{0}/nodes/{1}/NodeContext/status".format(_tc.integration_id,
                                                                    node_id),
                    "DOWN",
                    prevExist=False
                )            
        except etcd.EtcdAlreadyExist:
            pass

    return
