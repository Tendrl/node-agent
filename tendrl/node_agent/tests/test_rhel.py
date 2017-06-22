import platform
from tendrl.node_agent.discovery.platform.plugins import rhel


class TestRhel(object):
    def setup_method(self):
        self.obj = rhel.RHELPlugin()

    def test_discover_platform(self, monkeypatch):
        def mock_result():
            return ["rhel", "7.0"]
        monkeypatch.setattr(platform, "linux_distribution", mock_result)

        def mock_release():
            return "0.1"
        monkeypatch.setattr(platform, "release", mock_release)
        assert self.obj.discover_platform() == (
            {
                'Name': 'rhel',
                'OSVersion': '7.0',
                'KernelVersion': '0.1'
            })
