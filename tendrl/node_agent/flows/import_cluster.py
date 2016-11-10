from tendrl.node_agent.flows import Flow


class ImportCluster(Flow):
    def __init__(self, api_job):
        super(ImportCluster, self).__init__(api_job)
