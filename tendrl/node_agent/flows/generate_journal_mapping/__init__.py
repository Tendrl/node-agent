from tendrl.commons import flows
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.node_agent.provisioner.ceph import utils


class GenerateJournalMapping(flows.BaseFlow):
    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        if integration_id is None:
            raise FlowExecutionFailedError(
                "TendrlContext.integration_id cannot be empty"
            )

        # Generate the journal mapping for the nodes
        mapping = utils.generate_journal_mapping(
            self.parameters['Cluster.node_configuration']
        )
        for node_id in mapping.keys():
            journal_mapping = mapping[node_id]
            NS.node_agent.objects.JournalMapping(
                node_id=node_id,
                storage_disks=journal_mapping['storage_disks'],
                unallocated_disks=journal_mapping['unallocated_disks']
            ).save()
