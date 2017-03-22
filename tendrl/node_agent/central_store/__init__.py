from tendrl.commons import central_store


class NodeAgentEtcdCentralStore(central_store.EtcdCentralStore):
    def __init__(self):
        super(NodeAgentEtcdCentralStore, self).__init__()

    def save_nodecontext(self, node_context):
        NS.etcd_orm.save(node_context)

    def save_clusternodecontext(self, cluster_node_context):
        NS.etcd_orm.save(cluster_node_context)

    def save_config(self, config):
        NS.etcd_orm.save(config)

    def save_definition(self, definition):
        NS.etcd_orm.save(definition)

    def save_detectedcluster(self, detected_cluster):
        NS.etcd_orm.save(detected_cluster)

    def save_platform(self, platform):
        NS.etcd_orm.save(platform)

    def save_tendrlcontext(self, tendrl_context):
        NS.etcd_orm.save(tendrl_context)

    def save_service(self, service):
        NS.etcd_orm.save(service)

    def save_cpu(self, cpu):
        NS.etcd_orm.save(cpu)

    def save_disk(self, disk):
        NS.etcd_orm.save(disk)

    def save_file(self, file):
        NS.etcd_orm.save(file)

    def save_memory(self, memory):
        NS.etcd_orm.save(memory)

    def save_node(self, node):
        NS.etcd_orm.save(node)

    def save_os(self, os):
        NS.etcd_orm.save(os)

    def save_package(self, package):
        NS.etcd_orm.save(package)

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

    def save_job(self, job):
        NS.etcd_orm.save(job)

    def save_nodenetwork(self, network):
        NS.etcd_orm.save(network)

    def save_globalnetwork(self, network):
        NS.etcd_orm.save(network)
