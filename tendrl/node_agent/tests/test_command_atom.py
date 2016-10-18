from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleRunner
from tendrl.node_agent.atoms.generic.command \
    import Command


class Test_command_atom(object):
    def test_command_start(self, monkeypatch):

        def mock_runner_run(obj):
            return {"message": "test message"}, ""
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        c = Command()
        result, err = c.start({"key1": "value1", "key2": "value2"})

        assert result == {"message": "test message"}
        assert err == ""

    def test_command_error(self, monkeypatch):

        def mock_runner_run(obj):
            raise AnsibleExecutableGenerationFailed(
                "module_path", "arg",
                "err message"
            )
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        c = Command()
        result, err = c.start({"key1": "value1", "key2": "value2"})

        assert result == {}
        assert err == "Executabe could not be generated for module" \
            " module_path , with arguments arg. Error: err message"
