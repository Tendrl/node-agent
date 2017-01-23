import logging
import os

from tendrl.commons.etcdobj.etcdobj import EtcdObj

from tendrl.node_agent import objects


LOG = logging.getLogger(__name__)


class TendrlContext(objects.NodeAgentBaseObject):
    def __init__(self, integration_id=None, node_id=None, *args, **kwargs):
        super(TendrlContext, self).__init__(*args, **kwargs)

        self.value = 'nodes/%s/TendrlContext'

        # integration_id is the Tendrl generated cluster UUID
        self.node_id = node_id
        self.integration_id = integration_id or self._get_integration_id()

    def create_local_integration_id(self):
        tendrl_context_path = "~/.tendrl/" + self.value % self.node_id + \
                             "integration_id"
        with open(tendrl_context_path, 'wb+') as f:
            f.write(self.integration_id)
            LOG.info("SET_LOCAL: "
                     "tendrl_ns.node_agent.objects.TendrlContext.integration_id"
                     "==%s" %
                     self.integration_id)

    def _get_local_integration_id(self):
        try:
            tendrl_context_path = "~/.tendrl/" + self.value % self.node_id + \
                                 "integration_id"
            if os.path.isfile(tendrl_context_path):
                with open(tendrl_context_path) as f:
                    integration_id = f.read()
                    if integration_id:
                        LOG.info(
                            "GET_LOCAL: "
                            "tendrl_ns.node_agent.objects.TendrlContext"
                            ".integration_id==%s" % integration_id)
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
