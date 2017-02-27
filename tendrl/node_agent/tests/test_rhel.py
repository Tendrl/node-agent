import platform
from tendrl.node_agent.discovery.platform.plugins import rhel


class TestRhel(object):
    def setup_method(self, method):
        self.obj = rhel.RHELPlugin()

    def test_discover_platform(self, monkeypatch):
        def Mock_result():
            return ["rhel", "7.0"]
        monkeypatch.setattr(platform, "linux_distribution", Mock_result)

        def Mock_release():
            return "0.1"
        monkeypatch.setattr(platform, "release", Mock_release)
        assert self.obj.discover_platform() == (
            {
                'Name': 'rhel',
                'OSVersion': '7.0',
                'KernelVersion': '0.1'
            })
