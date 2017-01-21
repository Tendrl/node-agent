import importlib

import namespaces as ns
import yaml

from tendrl.commons.etcdobj.etcdobj import EtcdObj
from tendrl.commons.etcdobj import fields

from tendrl.node_agent.objects import node_agent_base_object
from tendrl.node_agent.objects.definition import master


# Definitions need there own special init, hence subclassing BaseObject
from tendrl.node_agent.persistence import etcd_utils


class Definition(node_agent_base_object.BaseObject):
    def __init__(self, *args, **kwargs):
        super(Definition, self).__init__(*args, **kwargs)

        self.value = '_tendrl/definitions/master'
        self.master = master.data
        self._parsed_defs = yaml.safe_load(self.master)

    def save(self):
        cls_etcd = etcd_utils.to_etcdobj(_DefinitionEtcd, self)
        tendrl_ns.persister.save_definition(cls_etcd())

    def load(self):
        cls_etcd = etcd_utils.to_etcdobj(_DefinitionEtcd, self)
        result = tendrl_ns.etcd_orm.read(cls_etcd())
        return result.to_tendrl_obj()

    def get_obj_definition(self, namespace, obj_name):
        raw_ns = "namespace.%s" % namespace
        raw_obj = self._get_parsed_defs()[raw_ns]['objects'][obj_name]
        for atom_name in raw_obj.get('atoms', {}).keys():
            atom_fqdn = "%s.objects.%s.atoms" % (namespace, obj_name)
            atom_cls = getattr(importlib.import_module(atom_fqdn), atom_name)
            tendrl_ns.add_atom(obj_name, atom_name, atom_cls)

        for flow_name in raw_obj.get('flows', {}).keys():
            flow_fqdn = "%s.objects.%s.flows" % (namespace, obj_name)
            flow_cls = getattr(importlib.import_module(flow_fqdn), flow_name)
            tendrl_ns.add_obj_flow(obj_name, flow_name, flow_cls)

        return ns.Namespace(attrs=raw_obj['attrs'],
                            enabled=raw_obj['enabled'],
                            obj_list=raw_obj['list'],
                            obj_value=raw_obj['value'],
                            atoms=raw_obj.get('atoms', {}),
                            flows=raw_obj.get('flows', {}),
                            help=raw_obj['help'])

    def get_flow_definition(self, namespace, flow_name):
        raw_ns = "namespace.%s" % namespace

        raw_flow = self._get_parsed_defs()[raw_ns]['flows'][flow_name]
        flow_fqdn = "%s.flows" % namespace
        flow_cls = getattr(importlib.import_module(flow_fqdn), flow_name)
        tendrl_ns.add_flow(flow_name, flow_cls)

        return ns.Namespace(atoms=raw_flow['atoms'],
                            help=raw_flow['help'],
                            enabled=raw_flow['enabled'],
                            inputs=raw_flow['inputs'],
                            pre_run=raw_flow['pre_run'],
                            post_run=raw_flow['post_run'],
                            type=raw_flow['type'],
                            uuid=raw_flow['uuid']
                            )


    def _get_parsed_defs(self):
        self._parsed_defs = yaml.safe_load(self.master)
        return self._parsed_defs

class _DefinitionEtcd(EtcdObj):
    """A table of the Definitions, lazily updated

    """
    __name__ = '_tendrl/definitions/master'

    def to_tendrl_obj(self):
        cls = _DefinitionEtcd
        result = Definition()
        for key in dir(cls):
            if not key.startswith('_'):
                attr = getattr(cls, key)
                if issubclass(attr.__class__, fields.Field):
                    setattr(result, key, attr.value)
        return result
