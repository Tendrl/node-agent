class SampleFlow(object):
    def __init__(self, api_job):
        self.api_job = api_job

    def start(self):
        return self.api_job['message']
