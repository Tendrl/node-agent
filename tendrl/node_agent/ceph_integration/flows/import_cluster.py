import json
import socket
import uuid

from tendrl.node_agent.config import TendrlConfig
from tendrl.node_agent.flows.flow import Flow

config = TendrlConfig()


class ImportCluster(Flow):
    def run(self):
        node_list = self.parameters['Node[]']
        if len(node_list) > 1:
            # This is the master node for this flow
            for node in node_list:
                if self.node_id != node:
                    new_params = self.parameters.copy()
                    new_params['Node[]'] = [node]
                # create same flow for each node in node list except $this
                    job = {"cluster_id": self.cluster_id,
                           "node_id": node,
                           "run": self.name,
                           "status": "new",
                           "parameters": new_params,
                           "parent": self.job['request_id'],
                           "type": "node"
                           }
                    self.etcd_client.write("/queue/%s" % uuid.uuid4(),
                                           json.dumps(job))
        if self.node_id in node_list:
            self.parameters['fqdn'] = socket.getfqdn()
            if config.get("node_agent", "deployment_type") == "production":
                self.parameters['Package.name'] = "tendrl-ceph-integration"
                self.parameters['Package.pkg_type'] = "yum"
            else:
                ceph = "git+https://github.com/Tendrl/" \
                       "ceph_integration.git@v1.0"
                self.parameters['Package.name'] = ceph

            self.parameters['Node.cmd_str'] = "tendrl-ceph-integration " \
                                              "--cluster-id %s" % \
                                              self.cluster_id
            tendrl_context = "nodes/%s/Tendrl_context/cluster_id" % \
                             self.node_id
            self.etcd_client.write(tendrl_context, self.cluster_id)
            return super(ImportCluster, self).run()
