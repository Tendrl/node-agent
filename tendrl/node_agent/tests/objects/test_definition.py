from mock import patch
import pkg_resources
from ruamel import yaml

from tendrl.node_agent.objects import definition


@patch.object(yaml, "safe_load")
@patch.object(pkg_resources, "resource_string")
def test_config(resource_str, safe_load):
    resource_str.return_value = "test"
    safe_load.return_value = {}
    obj = definition.Definition()
    if obj.data != "test":
        raise AssertionError()
    if not obj.get_parsed_defs() == {}:
        raise AssertionError()
