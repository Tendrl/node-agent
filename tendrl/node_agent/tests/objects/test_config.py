from mock import patch

from tendrl.commons import config as cmn_config
from tendrl.node_agent.objects import config


@patch.object(cmn_config, "load_config")
def test_config(load_config):
    load_config.return_value = "test"
    obj = config.Config()
    if obj.data != "test":
        raise AssertionError()
