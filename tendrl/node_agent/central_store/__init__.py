from tendrl.commons import central_store


class NodeAgentEtcdCentralStore(central_store.EtcdCentralStore):
    def __init__(self):
        super(NodeAgentEtcdCentralStore, self).__init__()

    def save_config(self, config):
        NS.etcd_orm.save(config)

    def save_compileddefinitions(self, compiled_definitions):
        NS.etcd_orm.save(compiled_definitions)

    def save_message(self, message):
        NS.etcd_orm.save(
            message,
            ttl=NS.config.data['message_retention_time'])

    def save_nodemessage(self, message):
        NS.etcd_orm.save(
            message,
            ttl=NS.config.data['message_retention_time']
        )

    def save_clustermessage(self, message):
        NS.etcd_orm.save(
            message,
            ttl=NS.config.data['message_retention_time']
        )

    def save_nodenetwork(self, network):
        NS.etcd_orm.save(network)

    def save_globalnetwork(self, network):
        NS.etcd_orm.save(network)
