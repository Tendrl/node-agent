import pytest
from tendrl.node_agent.atoms.generic.command \
    import Command
from tendrl.node_agent.flows.execute_command \
    import ExecuteCommand


sample_api_job = {
    "status": "processing", "sds_type": "gluster",
    "cluster_id": "49fa2adde8a6e98591f0f5cb4bc5f44d",
    "errors": {}, "attributes": {"_raw_params": "ls"},
    "message": "Executing command",
    "object_type": "generic",
    "flow": "ExecuteCommand"
}


class Test_ExecuteCommand_flow(object):
    def test_executeCommand_constructor(self):
        flow = ExecuteCommand(sample_api_job)
        assert flow.api_job == sample_api_job
        assert type(flow.atom) == type(Command)

    def Test_ExecuteCommand_Start(self, monkeypatch):
        flow = ExecuteCommand(sample_api_job)

        def mock_atom_start(attributes):
            return {"key1": "value1", "key2": "value2"}, ""
        monkeypatch.setattr(flow.atom, "start", mock_atom_start)

        result, err = flow.start()

        assert result == {"key1": "value1", "key2": "value2"}
        assert err == ""

    def Test_ExecuteCommand_Exception(self, monkeypatch):
        flow = ExecuteCommand(sample_api_job)

        def mock_atom_start(attributes):
            raise OSError("could not execute the command, no permission")
        monkeypatch.setattr(flow.atom, "start", mock_atom_start)

        pytest.raises(
            OSError,
            flow.start)
