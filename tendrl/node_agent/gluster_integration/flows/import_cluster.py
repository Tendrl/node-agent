import json
import socket
import uuid

from tendrl.commons.flows import base_flow
from tendrl.node_agent.manager import utils as manager_utils
from tendrl.commons.objects.job import Job


def get_package_name(installation_source_type):
    if installation_source_type in ["rpm", "deb"]:
        return "tendrl-gluster-integration"
    else:
        gluster = "git+https://github.com/Tendrl/" \
                  "gluster_integration.git@v1.1"
        return gluster


class ImportCluster(base_flow.BaseFlow):
    def run(self):
        curr_node_id = manager_utils.get_local_node_context()
        cluster_id = self.parameters['TendrlContext.integration_id']
        node_list = self.parameters['Node[]']
        if len(node_list) > 1:
            # This is the master node for this flow
            for node in node_list:
                if curr_node_id != node:
                    new_params = self.parameters.copy()
                    new_params['Node[]'] = [node]
                # create same flow for each node in node list except $this
                    payload = {"integration_id": cluster_id,
                               "node_id": node,
                               "run": self.name, "status": "new", "parameters":
                                   new_params, "parent": self.job['job_id'],
                               "type": "node"}
                    if "etcd_orm" in payload['parameters']:
                        del payload['parameters']['etcd_orm']
                    if "manager" in payload['parameters']:
                        del payload['parameters']['manager']

                    Job(job_id=str(uuid.uuid4()),
                        status="new",
                        payload=json.dumps(payload)).save()

        if curr_node_id in node_list:
            self.parameters['fqdn'] = socket.getfqdn()
            installation_source_type = self.config.get(
                "node-agent",
                "installation_source_type"
            )
            self.parameters['Package.pkg_type'] = installation_source_type
            self.parameters['Package.name'] = get_package_name(
                installation_source_type)
            self.parameters['Node.cmd_str'] = "tendrl-gluster-integration " \
                                              "--cluster-id %s" % \
                                              cluster_id
            tendrl_context = "nodes/%s/TendrlContext/cluster_id" % \
                             curr_node_id
            self.etcd_orm.client.write(tendrl_context, cluster_id)
            return super(ImportCluster, self).run()
