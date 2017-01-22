from tendrl.commons.persistence.etcd_persister import EtcdPersister


class NodeAgentEtcdPersister(EtcdPersister):
    def __init__(self, config):
        super(NodeAgentEtcdPersister, self).__init__(config)

    def save_node_context(self, node_context):
        tendrl_ns.etcd_orm.save(node_context)

    def save_config(self, config):
        tendrl_ns.etcd_orm.save(config)

    def update_cpu(self, cpu):
        self._store.save(cpu)

    def update_memory(self, memory):
        self._store.save(memory)

    def update_os(self, os):
        self._store.save(os)

    def update_service(self, service):
        self._store.save(service)

    def update_node(self, fqdn):
        self._store.save(fqdn)

    def update_node_context(self, context):
        self._store.save(context)

    def update_tendrl_context(self, context):
        self._store.save(context)

    def update_tendrl_definitions(self, definition):
        self._store.save(definition)

    def update_platform(self, platform):
        self._store.save(platform)
