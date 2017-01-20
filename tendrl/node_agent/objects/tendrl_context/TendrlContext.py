import logging
import os

from tendrl.commons.etcdobj.etcdobj import EtcdObj
from tendrl.commons.etcdobj import fields

from tendrl.node_agent.objects import base_object
from tendrl.node_agent.persistence import etcd_utils


LOG = logging.getLogger(__name__)


class TendrlContext(base_object.NodeAgentObject):
    def __init__(self, integration_id=None, node_id=None, *args, **kwargs):
        super(TendrlContext, self).__init__(*args, **kwargs)

        self.value = 'nodes/%s/TendrlContext'

        # integration_id is the Tendrl generated cluster UUID
        self.integration_id = integration_id or self._get_integration_id()
        self.node_id = node_id

    def save(self, persister):
        cls_etcd = etcd_utils.to_etcdobj(_TendrlContextEtcd, self)
        persister.save_node_context(cls_etcd())

    def load(self):
        cls_etcd = etcd_utils.to_etcdobj(_TendrlContextEtcd, self)
        result = tendrl_ns.etcd_orm.read(cls_etcd())
        return result.to_tendrl_obj()

    def _create_integration_id(self, integration_id=None):
        integration_id = "~/.tendrl/" + self.value % self.node_id + \
                             "integration_id"
        with open(integration_id, 'wb+') as f:
            f.write(integration_id)
            LOG.info("SET_LOCAL: "
                     "tendrl_ns.node_agent.objects.TendrlContext.integration_id"
                     "==%s" %
                     self.node_id)

    def _get_integration_id(self):
        try:
            integration_id = "~/.tendrl/" + self.value % self.node_id + \
                                 "integration_id"
            if os.path.isfile(integration_id):
                with open(integration_id) as f:
                    node_id = f.read()
                    if integration_id:
                        LOG.info(
                            "GET_LOCAL: "
                            "tendrl_ns.node_agent.objects.TendrlContext"
                            ".integration_id==%s" % node_id)
                        return integration_id
        except AttributeError:
            return None


class _TendrlContextEtcd(EtcdObj):
    """A table of the node context, lazily updated

    """
    __name__ = 'nodes/%s/TendrlContext'

    def render(self):
        self.__name__ = self.__name__ % self.node_id
        return super(_TendrlContextEtcd, self).render()

    def to_tendrl_obj(self):
        cls  = _TendrlContextEtcd
        result = TendrlContext()
        for key in dir(cls):
            if not key.startswith('_'):
                attr = getattr(cls, key)
                if issubclass(attr.__class__, fields.Field):
                    setattr(result, key, attr.value)
        return result

# Register Tendrl object in the current namespace (tendrl_ns.node_agent)
tendrl_ns.add_object(TendrlContext, TendrlContext.__name__)
