from mock import MagicMock
import sys
sys.modules['tendrl.common.config'] = MagicMock()
from tendrl.node_agent.ceph_integration.flows.import_cluster \
    import get_package_name
del sys.modules['tendrl.common.config']


class TestImportCephCluster(object):
    def test_get_package_name_for_rpm(self):
        actual_result = get_package_name("rpm")
        expected_result = "tendrl-ceph-integration"
        assert actual_result == expected_result

    def test_get_package_name_for_pip(self):
        actual_result = get_package_name("pip")
        expected_result = "git+https://github.com/Tendrl/" \
                          "ceph_integration.git@v1.1"
        assert actual_result == expected_result
