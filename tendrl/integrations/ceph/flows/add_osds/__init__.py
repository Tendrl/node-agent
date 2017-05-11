from tendrl.commons import flows
from tendrl.commons.event import Event
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.create_cluster import \
    ceph_help as create_ceph_help
from tendrl.commons.flows.expand_cluster import ceph_help
from tendrl.commons.message import Message


class AddOsds(flows.BaseFlow):
    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        if integration_id is None:
            raise FlowExecutionFailedError("TendrlContext.integration_id cannot be empty")

        Event(
            Message(
                job_id=self.parameters['job_id'],
                flow_id = self.parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={
                    "message": "Adding OSDs to ceph cluster %s" % integration_id
                }
            )
        )
        add_osds(self.parameters)

def add_osds(parameters):
    # Get the list of existing mons
    created_mons = ceph_help.existing_mons(parameters)

    osd_ips = []
    for node, config in parameters["Cluster.node_configuration"].iteritems():
        osd_ips.append(config["provisioning_ip"])

    # If osds passed create and add them
    if len(osd_ips) > 0:
        Event(
            Message(
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={
                    "message": "Creating OSDs on nodes: %s of cluster: %s" %\
                    (
                        str(osd_ips),
                        parameters['TendrlContext.integration_id']
                    )
                }
            )
        )
        create_ceph_help.create_osds(parameters, created_mons)
        Event(
            Message(
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={
                    "message": "Created OSDs on nodes: %s of cluster: %s" %\
                    (
                        str(osd_ips),
                        parameters['TendrlContext.integration_id']
                    )
                }
            )
        )
