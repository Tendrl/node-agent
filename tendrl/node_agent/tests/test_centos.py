import platform
from tendrl.node_agent.discovery.platform.plugins import centos


class TestCentos(object):
    def setup_method(self):
        self.obj = centos.CentosPlugin()

    def test_discover_platform(self, monkeypatch):
        def mock_result():
            return ["centos", "7.0"]
        monkeypatch.setattr(platform, "linux_distribution", mock_result)

        def mock_release():
            return "0.1"
        monkeypatch.setattr(platform, "release", mock_release)
        assert self.obj.discover_platform() == (
            {
                'Name': 'centos',
                'OSVersion': '7.0',
                'KernelVersion': '0.1'
            })
