import etcd

from tendrl.commons.utils import etcd_utils


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
            _node_context = NS.tendrl.objects.NodeContext(node_id=node_id).load()
            _tc = NS.tendrl.objects.TendrlContext(node_id=node_id).load()
            _cluster = NS.tendrl.objects.Cluster(integration_id=_tc.integration_id).load()
            
            # Remove stale provisioner tag
            if _cluster.is_managed == "yes":
                _tag = "provisioner/%s" % _cluster.integration_id
                if _tag in _node_context.tags:
                    _index_key = "/indexes/tags/%s" % _tag
                    _node_context.tags.remove(_tag)
                    _node_context.save()
                    etcd_utils.delete(_index_key)
                    
        except etcd.EtcdAlreadyExist:
            pass
    return
