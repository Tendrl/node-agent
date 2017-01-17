from mock import MagicMock
import sys
sys.modules['tendrl.commons.config'] = MagicMock()
from tendrl.commons.utils.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.commons.utils.ansible_module_runner \
    import AnsibleRunner
from tendrl.commons.utils import cmd_utils

del sys.modules['tendrl.commons.config']


class Test_command_atom(object):
    def test_command_start(self, monkeypatch):

        def mock_runner_run(obj):
            return {"message": "test message"}, ""
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        c = cmd_utils.Command('cmd')
        result, err, rc = c.run('/tmp/')

        assert result == {"message": "test message"}
        assert err == ""

    def test_command_error(self, monkeypatch):

        def mock_runner_run(obj):
            raise AnsibleExecutableGenerationFailed(
                "module_path", "arg",
                "err message"
            )
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        c = cmd_utils.Command('cmd')
        result, err, rc = c.run('/tmp/')

        assert result == {}
        assert err == "Executabe could not be generated for module" \
            " module_path , with arguments arg. Error: err message"
