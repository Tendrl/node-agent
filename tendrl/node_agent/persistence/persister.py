from tendrl.common.persistence.etcd_persister import EtcdPersister
from tendrl.common.persistence.file_persister import FilePersister


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


class NodeAgentFilePersister(FilePersister):
    def __init__(self, config):
        super(NodeAgentFilePersister, self).__init__(config)
        self._doc_location = "%s/node_agent" % \
            config.get("node_agent", "doc_persist_location")

    def update_cpu(self, cpu):
        f = open(
            "%s/%s" % (self._doc_location, cpu.__name__),
            "w"
        )
        f.write(cpu.json())
        f.close()

    def update_memory(self, memory):
        f = open(
            "%s/%s" % (self._doc_location, memory.__name__),
            "w"
        )
        f.write(memory.json())
        f.close()

    def update_os(self, os):
        f = open(
            "%s/%s" % (self._doc_location, os.__name__),
            "w"
        )
        f.write(os.json())
        f.close()

    def update_node(self, fqdn):
        f = open(
            "%s/%s" % (self._doc_location, fqdn.__name__),
            "w"
        )
        f.write(fqdn.json())
        f.close()

    def update_node_context(self, context):
        f = open(
            "%s/%s" % (self._doc_location, context.__name__),
            "w"
        )
        f.write(context.json())
        f.close()

    def update_tendrl_context(self, context):
        f = open(
            "%s/%s" % (self._doc_location, context.__name__),
            "w"
        )
        f.write(context.json())
        f.close()

    def update_tendrl_definitions(self, definition):
        f = open(
            "%s/%s" % (self._doc_location, definition.__name__),
            "w"
        )
        f.write(definition.json())
        f.close()
