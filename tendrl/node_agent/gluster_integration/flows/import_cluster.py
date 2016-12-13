import json
import socket
import uuid

from tendrl.common.flows.base_flow import BaseFlow
from tendrl.node_agent.manager import utils as manager_utils


def get_package_name(installation_source_type):
    if installation_source_type in ["rpm", "deb"]:
        return "tendrl-gluster-integration"
    else:
        gluster = "git+https://github.com/Tendrl/" \
                  "gluster_integration.git@v1.1"
        return gluster


class ImportCluster(BaseFlow):
    def run(self):
        curr_node_id = manager_utils.get_local_node_context()
        cluster_id = self.parameters['Tendrl_context.cluster_id']
        node_list = self.parameters['Node[]']
        if len(node_list) > 1:
            # This is the master node for this flow
            for node in node_list:
                if curr_node_id != node:
                    new_params = self.parameters.copy()
                    new_params['Node[]'] = [node]
                # create same flow for each node in node list except $this
                    job = {"cluster_id": cluster_id,
                           "node_id": node,
                           "run": self.name, "status": "new", "parameters":
                               new_params, "parent": self.job['request_id'],
                           "type": "node"}
                    if "etcd_client" in job['parameters']:
                        del job['parameters']['etcd_client']
                    self.etcd_client.write("/queue/%s" % uuid.uuid4(),
                                           json.dumps(job))
        if curr_node_id in node_list:
            self.parameters['fqdn'] = socket.getfqdn()
            installation_source_type = self.config.get(
                "node_agent",
                "installation_source_type"
            )
            self.parameters['Package.pkg_type'] = installation_source_type
            self.parameters['Package.name'] = get_package_name(
                installation_source_type)
            self.parameters['Node.cmd_str'] = "tendrl-gluster-integration " \
                                              "--cluster-id %s" % \
                                              cluster_id
            tendrl_context = "nodes/%s/Tendrl_context/cluster_id" % \
                             curr_node_id
            self.etcd_client.write(tendrl_context, cluster_id)
            return super(ImportCluster, self).run()
