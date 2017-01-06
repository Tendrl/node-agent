from tendrl.commons.persistence.etcd_persister import EtcdPersister


class NodeAgentEtcdPersister(EtcdPersister):
    def __init__(self, config):
        super(NodeAgentEtcdPersister, self).__init__(config)
        self._store = self.get_store()

    def update_cpu(self, cpu):
        self._store.save(cpu)

    def update_memory(self, memory):
        self._store.save(memory)

    def update_os(self, os):
        self._store.save(os)

    def update_node(self, fqdn):
        self._store.save(fqdn)

    def update_node_context(self, context):
        self._store.save(context)

    def update_tendrl_context(self, context):
        self._store.save(context)

    def update_tendrl_definitions(self, definition):
        self._store.save(definition)
