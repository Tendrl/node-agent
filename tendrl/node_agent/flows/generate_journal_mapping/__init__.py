import json

from tendrl.commons import flows
from tendrl.commons.objects.job import Job
from tendrl.node_agent.provisioner.ceph import utils


class GenerateJournalMapping(flows.BaseFlow):
    def run(self):
        # Generate the journal mapping for the nodes
        mapping = utils.generate_journal_mapping(
            self.parameters['Cluster.node_configuration'],
            integration_id=self.parameters.get("TendrlContext.integration_id")
        )

        # Update output dict
        job = Job(job_id=self.job_id).load()
        job.output[self.__class__.__name__] = json.dumps(mapping)
        job.save()
