from mock import patch
import pkg_resources
from ruamel import yaml

from tendrl.node_agent.objects import compiled_definition


@patch.object(yaml, "safe_load")
@patch.object(yaml, "safe_dump")
@patch.object(pkg_resources, "resource_string")
def test_compiled_definition(resource_str, safe_dump, safe_load):
    resource_str.return_value = "test"
    safe_load.return_value = {}
    safe_dump.return_value = {}
    obj = compiled_definition.CompiledDefinitions()
    if obj.data is not "":
        raise AssertionError()
    if not obj.get_parsed_defs() == {}:
        raise AssertionError()
    obj.merge_definitions([])
    if not compiled_definition.definitions.data == {}:
        raise AssertionError()
