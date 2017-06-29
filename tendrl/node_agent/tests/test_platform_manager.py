from mock import MagicMock
import os
import pytest
import sys
from tendrl.node_agent.discovery.platform import manager


class TestPlatformManager(object):
    def test_platform_manager_error(self, monkeypatch):
        def mock_listdir():
            return ["pytest.py"]
        monkeypatch.setattr(os, "listdir", mock_listdir)
        with pytest.raises(ValueError):
            self.manager = manager.PlatformManager()

    def test_platform_manager(self):
        sys.modules[
            'tendrl.node_agent.discovery.platform.plugins'
            ] = MagicMock()
        manager.importlib = MagicMock()
        self.manager = manager.PlatformManager()
        del sys.modules[
            'tendrl.node_agent.discovery.platform.plugins']
        assert isinstance(self.manager, manager.PlatformManager)

    def test_get_available_plugins(self):
        sys.modules[
            'tendrl.node_agent.discovery.platform.plugins'
            ] = MagicMock()
        self.manager = manager.PlatformManager()
        del sys.modules[
            'tendrl.node_agent.discovery.platform.plugins']
        assert type(self.manager.get_available_plugins()) is list
