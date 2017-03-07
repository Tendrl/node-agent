from tendrl.commons import etcdobj
from tendrl.commons import objects
import yaml


# Definitions need there own special init and have to be present in the NS
# before anything else, Hence subclassing BaseObject
from tendrl.node_agent.objects.compiled_definition import definitions


class CompiledDefinitions(objects.BaseObject):
    def __init__(self, *args, **kwargs):
        super(CompiledDefinitions, self).__init__(*args, **kwargs)

        self.value = '_NS/node_agent/compiled_definitions'
        self.data = definitions.data
        self._parsed_defs = yaml.safe_load(self.data)
        self._etcd_cls = _CompiledDefinitionsEtcd

    def get_parsed_defs(self):
        self._parsed_defs = yaml.safe_load(self.data)
        return self._parsed_defs

    def load_definition(self):
        return {}

    def merge_definitions(self, defs):
        compiled_defs = {}
        for definition in defs:
            compiled_defs.update(definition.get_parsed_defs())
        self.data = yaml.safe_dump(compiled_defs, default_flow_style=False)
        definition.data = self.data

class _CompiledDefinitionsEtcd(etcdobj.EtcdObj):
    """A table of the CompiledDefinitions, lazily updated

    """
    __name__ = '_NS/node_agent/compiled_definitions'
    _tendrl_cls = CompiledDefinitions
