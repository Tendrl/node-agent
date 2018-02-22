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
sys.modules['utils'] = utils
from tendrl.node_agent.monitoring.collectd.collectors.gluster. \
    low_weight import tendrl_glusterfs_brick_utilization as brick_utilization
del sys.modules['utils']
del sys.modules['collectd']
del sys.modules['tendrl_gluster']


class TestTendrlGlusterfsBrickUtilization(object):
    @patch("tendrl.node_agent.monitoring.collectd.collectors."
           "gluster.utils.exec_command")
    @patch("tendrl.node_agent.monitoring.collectd.collectors."
           "gluster.utils.ini2json")
    @patch("subprocess.Popen.communicate")
    @patch("tendrl.node_agent.monitoring.collectd.collectors."
           "gluster.low_weight.tendrl_glusterfs_brick_utilization."
           "os.statvfs")
    @patch("tendrl.node_agent.monitoring.collectd.collectors."
           "gluster.low_weight.tendrl_glusterfs_brick_utilization."
           "os.path.ismount")
    @patch("tendrl.node_agent.monitoring.collectd.collectors."
           "gluster.low_weight.tendrl_glusterfs_brick_utilization."
           "os.path.realpath")
    def test_gluster_brick_utilization(self,
                                       dirname,
                                       ismount,
                                       statvfs,
                                       communicate,
                                       ini2json,
                                       execu):
        gluster_state = mock_gluster_state.gluster_state()
        execu.return_value = ("pytest", "")
        ini2json.ini_to_dict.return_value = gluster_state
        obj = brick_utilization.TendrlBrickUtilizationPlugin()
        obj.CLUSTER_TOPOLOGY = utils.get_gluster_cluster_topology()
        obj.parse_proc_mounts = MagicMock(
            return_value=self.parse_proc_mounts()
        )
        communicate.return_value = self.communicate()
        ismount.return_value = True
        dirname.return_value = (['/'])
        mock_obj = MagicMock()
        mock_obj.f_bsize = 4096
        mock_obj.f_frsize = 4096
        mock_obj.f_blocks = 2093568
        mock_obj.f_bfree = 1351644
        mock_obj.f_bavail = 1351644
        mock_obj.f_files = 4192256
        mock_obj.f_ffree = 4101251
        mock_obj.f_favail = 4101251
        mock_obj.f_flag = 4096
        mock_obj.f_namemax = 255
        statvfs.return_value = mock_obj
        with open("tendrl/node_agent/tests/output/"
                  "tendrl_glusterfs_brick_utilization_output.json"
                  ) as f:
            assert obj.get_metrics() == json.loads(f.read())

    def communicate(self):
        with open("tendrl/node_agent/tests/"
                  "samples/lvs_sample.txt") as f:
            return f.read(), None

    def parse_proc_mounts(self):
        with open(
            "tendrl/node_agent/tests/samples/"
                "mount_point_state_sample.json") as f:
            return json.load(f)
