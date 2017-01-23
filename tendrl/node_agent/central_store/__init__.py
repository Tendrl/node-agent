from tendrl.commons import central_store


class NodeAgentEtcdCentralStore(central_store.EtcdCentralStore):
    def __init__(self):
        super(NodeAgentEtcdCentralStore, self).__init__()

    def save_nodecontext(self, node_context):
        tendrl_ns.etcd_orm.save(node_context)

    def save_config(self, config):
        tendrl_ns.etcd_orm.save(config)

    def save_definition(self, definition):
        tendrl_ns.etcd_orm.save(definition)

    def save_detectedcluster(self, detected_cluster):
        tendrl_ns.etcd_orm.save(detected_cluster)
