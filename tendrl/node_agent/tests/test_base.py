import pytest
from tendrl.node_agent.discovery.platform import base


class TestBase(object):
    def test_base(self):
        self.obj = base.PlatformDiscoverPlugin()
        with pytest.raises(NotImplementedError):
            self.obj.discover_platform()
