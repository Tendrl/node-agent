import ConfigParser
import os
import pytest
from tendrl.node_agent import config
from tendrl.node_agent.config import CONFIG_PATH_VAR
from tendrl.node_agent.config import ConfigNotFound


class Test_TendrlConfig(object):
    def test_valid_path_from_environment(self, monkeypatch):

        monkeypatch.setenv(CONFIG_PATH_VAR,
                           "/etc/tendrl/tendrl-environ.conf")

        def mock_os_path(path):
            return True
        monkeypatch.setattr(os.path, 'exists', mock_os_path)

        def mock_config_parser_read(obj, path):
            return
        monkeypatch.setattr(ConfigParser.SafeConfigParser,
                            'read', mock_config_parser_read)

        conf = config.TendrlConfig()

        assert conf.path == "/etc/tendrl/tendrl-environ.conf"

    def test_valid_path_from_default_path(self, monkeypatch):
        def mock_os_path(path):
            return True
        monkeypatch.setattr(os.path, 'exists', mock_os_path)

        def mock_config_parser_read(obj, path):
            return
        monkeypatch.setattr(ConfigParser.SafeConfigParser,
                            'read', mock_config_parser_read)

        conf = config.TendrlConfig()

        assert conf.path == "/etc/tendrl/tendrl.conf"

    def test_invalid_config_file_path(self, monkeypatch):
        def mock_os_path(path):
            return False
        monkeypatch.setattr(os.path, 'exists', mock_os_path)

        pytest.raises(
            ConfigNotFound,
            config.TendrlConfig
        )
