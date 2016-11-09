from mock import MagicMock
import sys
sys.modules['tendrl.node_agent.config'] = MagicMock()

import ansible.executor.module_common as module_common
from ansible import modules
import os
import pytest
from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleRunner
from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import config as cnf
del sys.modules['tendrl.node_agent.config']


class Test_ansible_runner_constructor(object):
    def test_invalid_module_path(self, monkeypatch):
        def mock_config_get(package, parameter):
                return "/tmp/.tendrl_runner"
        monkeypatch.setattr(cnf, 'get', mock_config_get)

        pytest.raises(
            ValueError,
            AnsibleRunner,
            "invalid/module/path",
            key1="value1",
            key2="value2"
        )

    def test_insufficient_arguments(self, monkeypatch):

        def mock_config_get(package, parameter):
                return "/tmp/.tendrl_runner"
        monkeypatch.setattr(cnf, 'get', mock_config_get)

        pytest.raises(
            ValueError,
            AnsibleRunner,
            "core/commands/command.py"
        )

    def test_successful_ansible_runner(self, monkeypatch):
        def mock_config_get(package, parameter):
                return "/tmp/.tendrl_runner"
        monkeypatch.setattr(cnf, 'get', mock_config_get)

        runner = AnsibleRunner(
            "core/commands/command.py",
            key1="value1",
            key2="value2",
        )
        assert runner.module_path == modules.__path__[0] + "/" +  \
            "core/commands/command.py"
        assert runner.argument_dict == {"key1": "value1",
                                        "key2": "value2"}


class Test_ansible_runner(object):
    def test_module_executable_generation_failed(self, monkeypatch):
        def mock_config_get(package, parameter):
                return "/tmp/.tendrl_runner"
        monkeypatch.setattr(cnf, 'get', mock_config_get)

        def mockreturn(path):
            return True
        monkeypatch.setattr(os.path, 'isfile', mockreturn)

        runner = AnsibleRunner(
            "/tmp/testansiblemodulefile",
            key1="value1",
            key2="value2"
        )
        pytest.raises(
            AnsibleExecutableGenerationFailed,
            runner.run
        )

    def test_module_run(self, monkeypatch):
        def mock_config_get(package, parameter):
                return "/tmp/.tendrl_runner"
        monkeypatch.setattr(cnf, 'get', mock_config_get)

        def mock_modify_module(modname, modpath, argument, task_vars={}):
            return ("echo \'{\"key\":\"test message\"}\'",
                    "new", "#! /usr/bin/sh")
        monkeypatch.setattr(module_common,
                            'modify_module', mock_modify_module)

        def mock_isfile(path):
            return True
        monkeypatch.setattr(os.path, 'isfile', mock_isfile)

        runner = AnsibleRunner(
            "/tmp/testansiblemodulefile",
            key1="value1",
            key2="value2"
        )

        out, err = runner.run()
        assert out == {"key": "test message"}
        assert err == ""
