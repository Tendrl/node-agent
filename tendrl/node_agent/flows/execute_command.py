from tendrl.node_agent.atoms.generic.command import Command


class ExecuteCommand(object):
    def __init__(self, api_job):
        super(ExecuteCommand, self).__init__()
        self.api_job = api_job
        self.atom = Command

    def start(self):
        attributes = self.api_job['attributes']
        result, err = self.atom().start(attributes)
        return result, err
