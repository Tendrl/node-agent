from tendrl.node_agent.atoms.generic.command import Command
from tendrl.node_agent.flows.flow_execution_exception import \
    FlowExecutionFailedError


class ExecuteCommand(object):
    def __init__(self, api_job):
        self.api_job = api_job
        self.atom = Command

    def start(self):
        attributes = self.api_job['attributes']
        try:
            result, err = self.atom().start(attributes)
        except Exception as e:
            raise FlowExecutionFailedError(str(e))
        return result, err
