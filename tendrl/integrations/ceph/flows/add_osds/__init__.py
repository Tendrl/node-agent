import gevent
import uuid

from tendrl.commons import flows
from tendrl.commons.event import Event
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.create_cluster import \
    ceph_help as create_ceph_help
from tendrl.commons.flows.expand_cluster import ceph_help
from tendrl.commons.message import Message
from tendrl.commons.objects.job import Job


class AddOsds(flows.BaseFlow):
    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        if integration_id is None:
            raise FlowExecutionFailedError("TendrlContext.integration_id cannot be empty")
        if "Cluster.node_configuration" not in self.parameters.keys():
            raise FlowExecutionFailedError("Cluster.node_configuration cannot be empty")

        ssh_job_ids = []
        ssh_setup_script = NS.ceph_provisioner.get_plugin().setup()
        for node_id in self.parameters["Cluster.node_configuration"].keys():
            new_params = {}
            new_params['Node[]'] = [node_id]
            new_params['ssh_setup_script'] = ssh_setup_script
            payload = {
                "node_ids": [node_id],
                "run": "tendrl.flows.SetupSsh",
                "status": "new",
                "parameters": new_params,
                "parent": self.parameters['job_id'],
                "type": "node"
            }
            _job_id = str(uuid.uuid4())
            Job(job_id=_job_id,
                status="new",
                payload=payload).save()
            ssh_job_ids.append(_job_id)
            Event(
                Message(
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Created SSH setup job %s for node"
                        " %s" % (_job_id, node_id)
                    }
                )
            )
        while True:
            gevent.sleep(3)
            all_status = {}
            for job_id in ssh_job_ids:
                # noinspection PyUnresolvedReferences
                all_status[job_id] = NS._int.client.read("/queue/%s/status" % job_id).value

            _failed = {_jid: status for _jid, status in all_status.iteritems() if status == "failed"}
            if _failed:
                raise FlowExecutionFailedError(
                    "SSH setup failed for jobs %s cluster %s" %
                    (str(_failed), integration_id)
                )
            if all([status == "finished" for status in all_status.values()]):
                Event(
                    Message(
                        job_id=self.parameters['job_id'],
                        flow_id = self.parameters['flow_id'],
                        priority="info",
                        publisher=NS.publisher_id,
                        payload={
                            "message": "SSH setup completed for all nodes"
                        }
                    )
                )
                break
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
