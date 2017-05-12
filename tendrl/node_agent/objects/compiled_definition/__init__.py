from ruamel import yaml

from tendrl.commons import objects

# Definitions need there own special init and have to be present in the NS
# before anything else, Hence subclassing BaseObject
from tendrl.node_agent.objects.compiled_definition import definitions


class CompiledDefinitions(objects.BaseObject):
    internal = True

    def __init__(self, *args, **kwargs):
        self._defs = {}
        super(CompiledDefinitions, self).__init__(*args, **kwargs)

        self.data = definitions.data
        self._parsed_defs = yaml.safe_load(self.data)
        self.value = '_NS/node_agent/compiled_definitions'

    def get_parsed_defs(self):
        self._parsed_defs = yaml.safe_load(self.data)
        return self._parsed_defs

    def merge_definitions(self, defs):
        compiled_defs = {}
        for definition in defs:
            compiled_defs.update(definition.get_parsed_defs())
        self.data = yaml.safe_dump(compiled_defs, default_flow_style=False)
        definitions.data = self.data
