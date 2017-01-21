import logging
import os

from tendrl.commons.etcdobj import EtcdObj

from tendrl.node_agent import objects


LOG = logging.getLogger(__name__)


class TendrlContext(objects.NodeAgentBaseObject):
    def __init__(self, integration_id=None, node_id=None, sds_name=None,
                 sds_version=None, *args, **kwargs):
        super(TendrlContext, self).__init__(*args, **kwargs)

        self.value = 'nodes/%s/TendrlContext'

        # integration_id is the Tendrl generated cluster UUID
        self.integration_id = integration_id or self._get_integration_id()
        self.node_id = node_id
        sds_det = _get_sds_name_and_version()
        self.sds_name = sds_name or sds_det['sds_name']
        self.sds_version = sds_version or sds_det['sds_version']
        self._etcd_cls = _TendrlContextEtcd

    def _get_sds_name_and_version():
        tendrl_context = {"sds_name": "", "sds_version": ""}
        cmd = cmd_utils.Command("gluster --version")
        out, err, rc = cmd.run(tendrl_ns.config['tendrl_ansible_exec_file'])
        if out["rc"] == 0:
            nvr = out['stdout']
            tendrl_context["sds_name"] = nvr.split()[0]
            tendrl_context["sds_version"] = nvr.split()[1]
            return tendrl_context

        cmd = cmd_utils.Command("ceph --version")
        out, err, rc = cmd.run(config['tendrl_ansible_exec_file'])
        if out["rc"] == 0:
            nvr = out['stdout']
            tendrl_context["sds_name"] = nvr.split()[0]
            tendrl_context["sds_version"] = nvr.split()[2].split("-")[0]

        return tendrl_context


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
    """A table of the tendrl context, lazily updated

    """
    __name__ = 'nodes/%s/TendrlContext'

    def render(self):
        self.__name__ = self.__name__ % tendrl_ns.node_context.node_id
        return super(_TendrlContextEtcd, self).render()
