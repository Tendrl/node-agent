import etcd
import importlib
import json
import socket
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
    low_weight import tendrl_glusterfs_health_counters as health_counters
del sys.modules['utils']
del sys.modules['collectd']
del sys.modules['tendrl_gluster']


class TestTendrlGlusterfsHealthCounters(object):
    @patch("tendrl.node_agent.monitoring.collectd.collectors."
           "gluster.utils.exec_command")
    @patch("tendrl.node_agent.monitoring.collectd.collectors."
           "gluster.utils.ini2json")
    @patch("tendrl.node_agent.monitoring.collectd.collectors."
           "gluster.utils.find_brick_host")
    @patch.object(etcd, "Client")
    @patch.object(socket, "gethostbyname")
    def test_gluster_health_counters(self, gethostbyname, client,
                                     brick_host, ini2json, execu):
        gethostbyname.return_value = "10.70.41.169"
        client.return_value = etcd.Client()
        brick_host.return_value = "10.70.41.169"
        gluster_state = mock_gluster_state.gluster_state()
        execu.return_value = ("pytest", "")
        ini2json.ini_to_dict.return_value = gluster_state
        obj = health_counters.TendrlGlusterfsHealthCounters()
        obj.CLUSTER_TOPOLOGY = utils.get_gluster_cluster_topology()
        with open("tendrl/node_agent/tests/output/"
                  "tendrl_glusterfs_health_counters_outpout.json"
                  ) as f:
            assert obj.get_metrics() == json.loads(f.read())
