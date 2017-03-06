from tendrl.commons import central_store


class NodeAgentEtcdCentralStore(central_store.EtcdCentralStore):
    def __init__(self):
        super(NodeAgentEtcdCentralStore, self).__init__()

    def save_nodecontext(self, node_context):
        tendrl_ns.etcd_orm.save(node_context)

    def save_clusternodecontext(self, cluster_node_context):
        tendrl_ns.etcd_orm.save(cluster_node_context)

    def save_config(self, config):
        tendrl_ns.etcd_orm.save(config)

    def save_definition(self, definition):
        tendrl_ns.etcd_orm.save(definition)

    def save_detectedcluster(self, detected_cluster):
        tendrl_ns.etcd_orm.save(detected_cluster)

    def save_platform(self, platform):
        tendrl_ns.etcd_orm.save(platform)

    def save_tendrlcontext(self, tendrl_context):
        tendrl_ns.etcd_orm.save(tendrl_context)

    def save_service(self, service):
        tendrl_ns.etcd_orm.save(service)

    def save_cpu(self, cpu):
        tendrl_ns.etcd_orm.save(cpu)

    def save_disk(self, disk):
        tendrl_ns.etcd_orm.save(disk)

    def save_file(self, file):
        tendrl_ns.etcd_orm.save(file)

    def save_memory(self, memory):
        tendrl_ns.etcd_orm.save(memory)

    def save_node(self, node):
        tendrl_ns.etcd_orm.save(node)

    def save_os(self, os):
        tendrl_ns.etcd_orm.save(os)

    def save_package(self, package):
        tendrl_ns.etcd_orm.save(package)

    def save_message(self, message):
        tendrl_ns.etcd_orm.save(message)

    def save_nodemessage(self, message):
        tendrl_ns.etcd_orm.save(message)

    def save_clustermessage(self, message):
        tendrl_ns.etcd_orm.save(message)

    def save_job(self, job):
        tendrl_ns.etcd_orm.save(job)

    def save_nodenetwork(self, network):
        tendrl_ns.etcd_orm.save(network)

    def save_globalnetwork(self, network):
        tendrl_ns.etcd_orm.save(network)
