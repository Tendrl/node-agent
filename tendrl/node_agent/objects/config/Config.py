from tendrl.commons import config as cmn_config

from tendrl.node_agent.objects import base_object


class Config(base_object.BaseObject):
    def __init__(self, config=None, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)

        Tendrl.add_object(self, self.__class__.__name__)

        self.value = '_tendrl/config/node-agent/data'
        self.data = config or cmn_config.load_config(
            'node-agent',"/etc/tendrl/node-agent/node-agent.conf.yaml")