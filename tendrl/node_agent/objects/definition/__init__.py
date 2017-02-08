import maps
import yaml


from tendrl.commons import etcdobj
from tendrl.commons import objects

from tendrl.node_agent.objects.definition import master


# Definitions need there own special init and have to be present in the NS
# before anything else, Hence subclassing BaseObject


class Definition(objects.BaseObject):
    def __init__(self, *args, **kwargs):
        super(Definition, self).__init__(*args, **kwargs)

        self.value = '_tendrl/definitions'
        self.master = master.data
        self._parsed_defs = yaml.safe_load(self.master)
        self._etcd_cls = _DefinitionEtcd

    def get_obj_definition(self, namespace, obj_name):
        raw_ns = "namespace.%s" % namespace
        raw_obj = self._get_parsed_defs()[raw_ns]['objects'][obj_name]
        return maps.NamedDict(attrs=raw_obj['attrs'],
                              enabled=raw_obj['enabled'],
                              obj_list=raw_obj.get('list', ""),
                              obj_value=raw_obj['value'],
                              atoms=raw_obj.get('atoms', {}),
                              flows=raw_obj.get('flows', {}),
                              help=raw_obj['help']
                              )

    def get_flow_definition(self, namespace, flow_name):
        raw_ns = "namespace.%s" % namespace

        raw_flow = self._get_parsed_defs()[raw_ns]['flows'][flow_name]
        return maps.NamedDict(atoms=raw_flow['atoms'],
                              help=raw_flow['help'],
                              enabled=raw_flow['enabled'],
                              inputs=raw_flow['inputs'],
                              pre_run=raw_flow.get('pre_run', []),
                              post_run=raw_flow.get('post_run', []),
                              type=raw_flow['type'],
                              uuid=raw_flow['uuid'])

    def _get_parsed_defs(self):
        self._parsed_defs = yaml.safe_load(self.master)
        return self._parsed_defs


class _DefinitionEtcd(etcdobj.EtcdObj):
    """A table of the Definitions, lazily updated

    """
    __name__ = '_tendrl/definitions'
    _tendrl_cls = Definition
