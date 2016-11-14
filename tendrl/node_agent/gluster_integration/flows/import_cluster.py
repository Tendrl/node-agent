import json
import socket
import uuid

from tendrl.node_agent.flows.flow import Flow

class ImportCluster(Flow):
    def run(self):
        node_list = self.parameters['node[]']
        if len(node_list) > 1:
            # This is the master node for this flow
            for node in node_list:
                if self.node_id != node:
                    new_params = self.parameters.copy()
                    new_params['nodes[]'] = [node]
                # create same flow for each node in node list except $this
                    job = { "cluster_id": self.parameters['cluster_id'],
                            "node_id": node,
                            "run": self.name,
                            "status": "new",
                            "parameters": new_params,
                            "parent": self.job['request_id']
                    }
                    self.etcd_client.write("/queue/%s" % uuid.uuid4(),
                                           json.dumps(job))
        self.parameters['fqdn'] = socket.getfqdn()
        self.parameters['Package.name'] = " " \
                                          "git+https://github.com/Tendrl/gluster_integration"
#        self.parameters['Package.version'] = self.parameters[
#            'Tendrl_context.sds_version']
        self.parameters['Node.cmd_str'] = "tendrl-gluster-integration " \
                                          "--cluster-id %s" % self.parameters[
            'Tendrl_context.cluster_id']
        return super(ImportCluster, self).run()

