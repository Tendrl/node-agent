from tendrl.commons.persistence.etcd_persister import EtcdPersister


class NodeAgentEtcdPersister(EtcdPersister):
    def __init__(self, config):
        super(NodeAgentEtcdPersister, self).__init__(config)

    def save_node_context(self, node_context):
        NS.etcd_orm.save(node_context)

    def save_node(self, node):
        NS.etcd_orm.save(node)

    def save_tendrl_context(self, tendrl_context):
        NS.etcd_orm.save(tendrl_context)

    def save_config(self, config):
        NS.etcd_orm.save(config)

    def save_cpu(self, cpu):
        NS.etcd_orm.save(cpu)

    def save_os(self, os):
        NS.etcd_orm.save(os)

    def save_memory(self, memory):
        NS.etcd_orm.save(memory)

    def save_platform(self, platform):
        NS.etcd_orm.save(platform)

    def save_service(self, service):
        NS.etcd_orm.save(service)

    def save_disk(self, disk):
        NS.etcd_orm.save(disk)

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
