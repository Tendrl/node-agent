import json
import uuid

from tendrl.node_agent.flows.flow import Flow

class ImportCluster(Flow):
    def run(self):
        node_list = self.parameters['Nodes[]']
        if len(node_list) > 1:
            # This is the master node for this flow
            for node in node_list:
                if self.node_id != node:
                    new_params = self.parameters.copy()
                    new_params['Nodes[]'] = [node]
                # create same flow for each node in node list except $this
                    job = {
                            "cluster_id": self.parameters['cluster_id'],
                            "node_id": node,
                            "run": self.name,
                            "status": "new",
                            "parameters": new_params,
                            "type": "node"
                    }
                    self.etcd_client.write("/queue/%s" % uuid.uuid4(),
                                           json.dumps(job))

        super(ImportCluster, self).run()
