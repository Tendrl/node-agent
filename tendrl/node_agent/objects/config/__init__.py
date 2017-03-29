from tendrl.commons import config as cmn_config
from tendrl.commons import etcdobj
from tendrl.commons import objects


class Config(objects.BaseObject):
    internal = True
    def __init__(self, config=None, *args, **kwargs):
        self._defs = {}
        super(Config, self).__init__(*args, **kwargs)

        self.value = '_NS/node_agent/config'
        self.data = config or cmn_config.load_config(
            'node-agent', "/etc/tendrl/node-agent/node-agent.conf.yaml")
        self._etcd_cls = _ConfigEtcd

class _ConfigEtcd(etcdobj.EtcdObj):
    """Config etcd object, lazily updated

    """
    __name__ = '_NS/node_agent/config'
    _tendrl_cls = Config
