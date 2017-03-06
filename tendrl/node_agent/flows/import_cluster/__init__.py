import etcd
import gevent
import json
import uuid


from tendrl.node_agent import flows
from tendrl.node_agent.flows.import_cluster.ceph_help import import_ceph
from tendrl.node_agent.flows.import_cluster.gluster_help import import_gluster

from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.objects.job import Job


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
                if tendrl_ns.node_context.node_id != node:
                    new_params = self.parameters.copy()
                    new_params['Node[]'] = [node]
                    # create same flow for each node in node list except $this
                    Job(job_id=str(uuid.uuid4()),
                        integration_id=integration_id,
                        run="tendrl.node_agent.flows.ImportCluster",
                        status="new",
                        parameters=new_params,
                        type="node",
                        parent=self.parameters['request_id'],
                        node_ids=[node]).save()

                    Event(
                        Message(
                            priority="info",
                            publisher=tendrl_ns.publisher_id,
                            payload={
                                "message": "Import cluster job created on node"
                                " %s" % node
                            },
                            request_id=self.parameters['request_id'],
                            flow_id=self.uuid,
                            cluster_id=tendrl_ns.tendrl_context.integration_id,
                        )
                    )

        Event(
            Message(
                priority="info",
                publisher=tendrl_ns.publisher_id,
                payload={
                    "message": "Import cluster job started on node %s" %
                    tendrl_ns.node_context.fqdn
                },
                request_id=self.parameters['request_id'],
                flow_id=self.uuid,
                cluster_id=tendrl_ns.tendrl_context.integration_id,
            )
        )
        sds_name = self.parameters['DetectedCluster.sds_pkg_name']
        if "ceph" in sds_name.lower():
            node_context = tendrl_ns.node_context.load()
            if "mon" in node_context.tags:
                import_ceph(
                    tendrl_ns.tendrl_context.integration_id,
                    self.parameters['request_id'],
                    self.uuid
                )
        else:
            import_gluster(
                tendrl_ns.tendrl_context.integration_id,
                self.parameters['request_id'],
                self.uuid
            )

        # import cluster's run() should not return unless the new cluster entry
        # is updated in etcd, as the job is marked as finished if this
        # function is returned. This might lead to inconsistancy in the API
        # functionality. The below loop waits for the cluster details
        # to be updated in etcd.
        while True:
            gevent.sleep(2)
            try:
                tendrl_ns.etcd_orm.client.read("/clusters/%s" % integration_id)
                break
            except etcd.EtcdKeyNotFound:
                continue
