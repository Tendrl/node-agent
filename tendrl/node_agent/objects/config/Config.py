from tendrl.commons.etcdobj.etcdobj import EtcdObj
from tendrl.commons.etcdobj import fields
from tendrl.commons import config as cmn_config

from tendrl.node_agent.objects import node_agent_base_object
from tendrl.node_agent.persistence import etcd_utils



class Config(node_agent_base_object.NodeAgentObject):
    def __init__(self, config=None, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)

        self.value = '_tendrl/config/node-agent/data'
        self.data = config or cmn_config.load_config(
            'node-agent',"/etc/tendrl/node-agent/node-agent.conf.yaml")

    def save(self, persister):
        cls_etcd = etcd_utils.to_etcdobj(_ConfigEtcd, self)
        persister.save_config(cls_etcd())

    def load(self):
        cls_etcd = etcd_utils.to_etcdobj(_ConfigEtcd, self)
        result = tendrl_ns.etcd_orm.read(cls_etcd())
        return result.to_tendrl_obj()


class _ConfigEtcd(EtcdObj):
    """Config etcd object, lazily updated

    """
    __name__ = '_tendrl/condig/node-agent/'


    def to_tendrl_obj(self):
        cls = _ConfigEtcd
        result = Config()
        for key in dir(cls):
            if not key.startswith('_'):
                attr = getattr(cls, key)
                if issubclass(attr.__class__, fields.Field):
                    setattr(result, key, attr.value)
        return result


# Register Tendrl object in the current namespace (tendrl_ns.node_agent)
tendrl_ns.add_object(Config.__name__, Config)
