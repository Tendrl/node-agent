from tendrl.commons.etcdobj.etcdobj import EtcdObj
from tendrl.commons import config as cmn_config

from tendrl.node_agent.objects import base_object
from tendrl.node_agent.persistence import etcd_utils


class Config(base_object.BaseObject):
    def __init__(self, config=None, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)

        self.value = '_tendrl/config/node-agent/data'
        self.data = config or cmn_config.load_config(
            'node-agent',"/etc/tendrl/node-agent/node-agent.conf.yaml")

    def save(self, persister):
        cls_etcd = etcd_utils.to_etcdobj(_ConfigEtcd, self)
        persister.save_config(cls_etcd())


class _ConfigEtcd(EtcdObj):
    """Config etcd object, lazily updated

    """
    __name__ = '_tendrl/condig/node-agent/'
