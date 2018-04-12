import importlib
import json
import sys

from mock import MagicMock
from mock import patch
from tendrl.node_agent.tests import mock_gluster_state

sys.modules['tendrl_gluster'] = mock_gluster_state
sys.modules['collectd'] = MagicMock()
utils = importlib.import_module(
    "tendrl.node_agent."
    "monitoring.collectd.collectors.gluster.utils")
heavy_weight = importlib.import_module(
    "tendrl.node_agent."
    "monitoring.collectd.collectors.gluster.heavy_weight")
sys.modules['utils'] = utils
sys.modules['heavy_weight'] = heavy_weight
from tendrl.node_agent.monitoring.collectd.collectors.gluster. \
    heavy_weight import tendrl_glusterfs_profile_info as profile_info
del sys.modules['heavy_weight']
del sys.modules['utils']
del sys.modules['collectd']
del sys.modules['tendrl_gluster']


class TestTendrlGlusterfsProfileInfo(object):
    @patch("tendrl.node_agent.monitoring.collectd.collectors."
           "gluster.utils.exec_command")
    @patch("tendrl.node_agent.monitoring.collectd.collectors."
           "gluster.utils.ini2json")
    def test_gluster_profile_info(self, ini2json, execu):
        profile_info.tendrl_gluster_heal_info = MagicMock()
        profile_info.TendrlHealInfoAndProfileInfoPlugin.etcd_client = \
            MagicMock()
        gluster_state = mock_gluster_state.gluster_state()
        execu.return_value = self.volume_profile()
        ini2json.ini_to_dict.return_value = gluster_state
        utils.find_brick_host = MagicMock(return_value="10.70.43.214")
        obj = profile_info.TendrlHealInfoAndProfileInfoPlugin()
        obj.CLUSTER_TOPOLOGY = utils.get_gluster_cluster_topology()
        with open("tendrl/node_agent/tests/output/"
                  "tendrl_glusterfs_profile_info_output.json"
                  ) as f:
            assert obj.get_metrics() == json.loads(f.read())

    def volume_profile(self):
        with open("tendrl/node_agent/tests/samples/gluster_volume_"
                  "profile_sample.xml") as f:
            return f.read(), None
