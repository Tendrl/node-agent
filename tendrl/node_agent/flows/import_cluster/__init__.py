import json
import uuid


from tendrl.node_agent import flows
from tendrl.node_agent.flows.import_cluster.ceph_help import import_ceph
from tendrl.node_agent.flows.import_cluster.gluster_help import import_gluster


class ImportCluster(flows.NodeAgentBaseFlow):
    def run(self):
        self.pre_run = []
        self.atoms = []
        self.post_run = []

        integration_id = self.parameters['TendrlContext.integration_id']
        tendrl_ns.tendrl_context.integration_id = integration_id
        tendrl_ns.tendrl_context.save()
        node_list = self.parameters['Node[]']
        if len(node_list) > 1:
            # This is the master node for this flow
            for node in node_list:
                if tendrl_ns.node_contex.node_id != node:
                    new_params = self.parameters.copy()
                    new_params['Node[]'] = [node]
                # create same flow for each node in node list except $this
                    job = {"cluster_id": integration_id,
                           "node_ids": [node],
                           "run": "tendrl.node_agent.flows.ImportCluster",
                           "status": "new",
                           "parameters": new_params,
                           "parent": self.parameters['request_id'],
                           "type": "node"
                           }

                    tendrl_ns.etcd_orm.client.write("/queue/%s" % uuid.uuid4(),
                                               json.dumps(job))


        sds_name = self.parameters['DetectedCluster.sds_pkg_name']
        if "ceph" in sds_name.lower():
            import_ceph(tendrl_ns.tendrl_context.integration_id)
        else:
            import_gluster(tendrl_ns.tendrl_context.integration_id)
