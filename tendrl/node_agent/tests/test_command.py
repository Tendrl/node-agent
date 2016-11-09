from mock import MagicMock
import sys
sys.modules['tendrl.node_agent.config'] = MagicMock()
from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleRunner
from tendrl.node_agent.manager.command \
    import Command
del sys.modules['tendrl.node_agent.config']


class Test_command_atom(object):
    def test_command_start(self, monkeypatch):

        def mock_runner_run(obj):
            return {"message": "test message"}, ""
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        c = Command({"key1": "value1", "key2": "value2"})
        result, err = c.start()

        assert result == {"message": "test message"}
        assert err == ""

    def test_command_error(self, monkeypatch):

        def mock_runner_run(obj):
            raise AnsibleExecutableGenerationFailed(
                "module_path", "arg",
                "err message"
            )
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        c = Command({"key1": "value1", "key2": "value2"})
        result, err = c.start()

        assert result == {}
        assert err == "Executabe could not be generated for module" \
            " module_path , with arguments arg. Error: err message"
