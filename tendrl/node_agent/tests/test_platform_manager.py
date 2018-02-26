import mock
import os
import pytest
import sys

from tendrl.node_agent.discovery.platform import manager
from tendrl.node_agent.tests.test_init import init


class TestPlatformManager(object):
    def setup_method(self, method):
        init()

    def test_platform_manager_error(self, monkeypatch):
        def mock_listdir(path):
            return ["pytest.py"]
        monkeypatch.setattr(os, "listdir", mock_listdir)
        setattr(NS, "publisher_id", "node_agent")
        with pytest.raises(ValueError):
            self.manager = manager.PlatformManager()

    def test_platform_manager(self):
        sys.modules[
            'tendrl.node_agent.discovery.platform.plugins'
            ] = mock.MagicMock()
        manager.importlib = mock.MagicMock()
        self.manager = manager.PlatformManager()
        del sys.modules[
            'tendrl.node_agent.discovery.platform.plugins']
        assert isinstance(self.manager, manager.PlatformManager)

    def test_get_available_plugins(self):
        sys.modules[
            'tendrl.node_agent.discovery.platform.plugins'
            ] = mock.MagicMock()
        self.manager = manager.PlatformManager()
        del sys.modules[
            'tendrl.node_agent.discovery.platform.plugins']
        assert type(self.manager.get_available_plugins()) is list
