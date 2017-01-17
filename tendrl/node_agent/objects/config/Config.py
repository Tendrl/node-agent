from tendrl.commons import config as cmn_config

class Config(object):
    def __init__(self, config=None):
        self.path = '_tendrl/config/node-agent'
        self.data = config or cmn_config.load_config(
            'node-agent',"/etc/tendrl/node-agent/node-agent.conf.yaml")