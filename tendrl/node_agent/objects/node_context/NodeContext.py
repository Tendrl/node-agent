import logging
import os
import uuid

from tendrl.commons.etcdobj.etcdobj import EtcdObj
from tendrl.commons.etcdobj import fields
from tendrl.commons.utils import cmd_utils

from tendrl.node_agent.objects import base_object
from tendrl.node_agent.persistence import etcd_utils


LOG = logging.getLogger(__name__)


class NodeContext(base_object.NodeAgentObject):
    def __init__(self, machine_id=None, node_id=None, fqdn=None,
                 tags=None, status=None, *args, **kwargs):
        super(NodeContext, self).__init__(*args, **kwargs)

        self.value = 'nodes/%s/NodeContext'
        self.machine_id = machine_id or self._get_machine_id()
        self.node_id = node_id or self._get_node_id() or self.create_node_id
        self.fqdn = fqdn
        self.tags = tags
        self.status = status

    def save(self, persister):
        cls_etcd = etcd_utils.to_etcdobj(_NodeContextEtcd, self)
        persister.save_node_context(cls_etcd())

    def load(self):
        cls_etcd = etcd_utils.to_etcdobj(_NodeContextEtcd, self)
        result = tendrl_ns.etcd_orm.read(cls_etcd())
        return result.to_tendrl_obj()

    def _get_machine_id(self):
        cmd = cmd_utils.Command({"_raw_params": "cat /etc/machine-id"})
        out, err, rc = cmd.run(tendrl_ns.config['tendrl_ansible_exec_file'])
        return out['stdout']

    def _create_node_id(self, node_id=None):
        node_id = node_id or str(uuid.uuid4())
        local_node_context = "~/.tendrl/" + self.value % self.node_id + \
                             "/node_id"
        with open(local_node_context, 'wb+') as f:
            f.write(node_id)
            LOG.info("SET_LOCAL: "
                     "tendrl_ns.node_agent.objects.NodeContext.node_id==%s" %
                     self.node_id)

    def _get_node_id(self):
        try:
            local_node_context = "~/.tendrl/" + self.value % self.node_id + \
                                 "/node_id"
            if os.path.isfile(local_node_context):
                with open(local_node_context) as f:
                    node_id = f.read()
                    if node_id:
                        LOG.info(
                            "GET_LOCAL: tendrl_ns.node_agent.objects.NodeContext"
                            ".node_id==%s" % node_id)
                        return node_id
        except AttributeError:
            return None


class _NodeContextEtcd(EtcdObj):
    """A table of the node context, lazily updated

    """
    __name__ = 'nodes/%s/Node_context'

    def render(self):
        self.__name__ = self.__name__ % self.node_id
        return super(_NodeContextEtcd, self).render()

    def to_tendrl_obj(self):
        cls  = _NodeContextEtcd
        result = NodeContext()
        for key in dir(cls):
            if not key.startswith('_'):
                attr = getattr(cls, key)
                if issubclass(attr.__class__, fields.Field):
                    setattr(result, key, attr.value)
        return result

# Register Tendrl object in the current namespace (tendrl_ns.node_agent)
tendrl_ns.add_object(NodeContext, NodeContext.__name__)
