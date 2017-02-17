from tendrl.commons import config as cmn_config
from tendrl.commons import etcdobj

from tendrl.node_agent import objects


class Config(objects.NodeAgentBaseObject):
    def __init__(self, config=None, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)

        self.value = '_tendrl/config/node-agent'
        self.data = config or cmn_config.load_config(
            'node-agent', "/etc/tendrl/node-agent/node-agent.conf.yaml")
        self._etcd_cls = _ConfigEtcd


class _ConfigEtcd(etcdobj.EtcdObj):
    """Config etcd object, lazily updated

    """
    __name__ = '_tendrl/config/node-agent'
    _tendrl_cls = Config
