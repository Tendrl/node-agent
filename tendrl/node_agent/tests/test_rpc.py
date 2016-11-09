import etcd
import gevent.event
from mock import MagicMock
import pytest
from sample_manager import SampleManager
import sys
sys.modules['tendrl.node_agent.config'] = MagicMock()

from tendrl.node_agent.flows.flow_execution_exception import \
    FlowExecutionFailedError
from tendrl.node_agent.manager.rpc import config
from tendrl.node_agent.manager.rpc import EtcdRPC
from tendrl.node_agent.manager.rpc import EtcdThread
import uuid
del sys.modules['tendrl.node_agent.config']


class MockFlow(object):
    def __init__(self, api_job):
        self.api_job = api_job

    def start(self):
        return self.api_job['message']


class Test_EtcdRpc(object):
    def test_constructor(self, monkeypatch):
        def mock_config_get(package, parameter):
            if parameter == "etcd_port":
                return 2379
            elif parameter == "etcd_connection":
                return "0.0.0.0"
        monkeypatch.setattr(config, 'get', mock_config_get)

        def mock_uuid4():
            return 'aa22a6fe-87f0-45cf-8b70-2d0ff4c02af6'
        monkeypatch.setattr(uuid, 'uuid4', mock_uuid4)

        server = EtcdRPC()

        assert server.bridge_id == 'aa22a6fe-87f0-45cf-8b70-2d0ff4c02af6'
        local_client = etcd.Client(
            port=2379,
            host="0.0.0.0"
        )
        assert server.client.port == local_client.port
        assert server.client.host == local_client.host

    def test_convert_flow_name(self, monkeypatch):
        def mock_config_get(package, parameter):
            if parameter == "etcd_port":
                return 2379
            elif parameter == "etcd_connection":
                return "0.0.0.0"
        monkeypatch.setattr(config, 'get', mock_config_get)

        def mock_uuid4():
            return 'aa22a6fe-87f0-45cf-8b70-2d0ff4c02af6'
        monkeypatch.setattr(uuid, 'uuid4', mock_uuid4)

        server = EtcdRPC()

        assert server.convert_flow_name("ExecuteCommand") == "execute_command"
        assert server.convert_flow_name(
            "InstallDnfPackage") == "install_dnf_package"
        assert server.convert_flow_name("Create") == "create"

    def test_invoke_flow(self, monkeypatch):
        def mock_config_get(package, parameter):
            if parameter == "etcd_port":
                return 2379
            elif parameter == "etcd_connection":
                return "0.0.0.0"
        monkeypatch.setattr(config, 'get', mock_config_get)

        def mock_uuid4():
            return 'aa22a6fe-87f0-45cf-8b70-2d0ff4c02af6'
        monkeypatch.setattr(uuid, 'uuid4', mock_uuid4)

        server = EtcdRPC()
        api_job = {'message': "sample message"}
        result = server.invoke_flow(
            "SampleFlow", api_job,
            flow_module_path="tendrl.node_agent.tests"
        )
        assert result == "sample message"

    def test_stop(self):
        assert True

    def test_process_job_positive(self, monkeypatch):
        def mock_config_get(package, parameter):
            if parameter == "etcd_port":
                return 2379
            elif parameter == "etcd_connection":
                return "0.0.0.0"
        monkeypatch.setattr(config, 'get', mock_config_get)

        def mock_uuid4():
            return 'aa22a6fe-87f0-45cf-8b70-2d0ff4c02af6'
        monkeypatch.setattr(uuid, 'uuid4', mock_uuid4)

        server = EtcdRPC()

        def mock_etcd_write(key, value):
            pass
        monkeypatch.setattr(server.client, 'write', mock_etcd_write)

        def mock_invoke_flow(flow, job):
            return {"key1": "value1", "key2": "value2"}, ""
        monkeypatch.setattr(server, 'invoke_flow', mock_invoke_flow)

        input_raw_job1 = {
            "status": "new", "sds_type": "generic",
            "cluster_id": "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "errors": {}, "attributes": {"_raw_params": "ls"},
            "message": "Executing command",
            "type": "node",
            "object_type": "generic",
            "flow": "ExecuteCommand"
        }

        raw_job, executed = server._process_job(
            input_raw_job1,
            "9a9604c0-d2a6-4be0-9a82-262f10037a8f"
        )

        assert executed
        assert raw_job['status'] == "finished"
        assert raw_job['request_id'] == "aa22a6fe-87f0-45cf-8b70-2d0ff4c02af6"\
            "/flow_aa22a6fe-87f0-45cf-8b70-2d0ff4c02af6"
        assert raw_job["response"] == {
            "result": {"key1": "value1", "key2": "value2"},
            "error": ""
        }

        input_raw_job2 = {
            "status": "processing", "sds_type": "generic",
            "cluster_id": "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "errors": {}, "attributes": {"_raw_params": "ls"},
            "message": "Executing command",
            "type": "node",
            "object_type": "generic",
            "flow": "ExecuteCommand"
        }

        server = EtcdRPC()

        def mock_etcd_write(key, value):
            pass
        monkeypatch.setattr(server.client, 'write', mock_etcd_write)

        def mock_invoke_flow(flow, job):
            return {"key1": "value1", "key2": "value2"}, ""
        monkeypatch.setattr(server, 'invoke_flow', mock_invoke_flow)

        raw_job, executed = server._process_job(
            input_raw_job2,
            "9a9604c0-d2a6-4be0-9a82-262f10037a8f"
        )
        assert not executed

        input_raw_job3 = {
            "status": "new", "sds_type": "gluster",
            "cluster_id": "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "errors": {}, "attributes": {"_raw_params": "ls"},
            "message": "Executing command",
            "type": "sds",
            "object_type": "generic",
            "flow": "ExecuteCommand"
        }

        server = EtcdRPC()

        def mock_etcd_write(key, value):
            pass
        monkeypatch.setattr(server.client, 'write', mock_etcd_write)

        def mock_invoke_flow(flow, job):
            return {"key1": "value1", "key2": "value2"}, ""
        monkeypatch.setattr(server, 'invoke_flow', mock_invoke_flow)

        raw_job, executed = server._process_job(
            input_raw_job3,
            "9a9604c0-d2a6-4be0-9a82-262f10037a8f"
        )
        assert not executed

    def test_process_job_exception(self, monkeypatch):
        def mock_config_get(package, parameter):
            if parameter == "etcd_port":
                return 2379
            elif parameter == "etcd_connection":
                return "0.0.0.0"
        monkeypatch.setattr(config, 'get', mock_config_get)

        def mock_uuid4():
            return 'aa22a6fe-87f0-45cf-8b70-2d0ff4c02af6'
        monkeypatch.setattr(uuid, 'uuid4', mock_uuid4)

        server = EtcdRPC()

        def mock_etcd_write(key, value):
            pass
        monkeypatch.setattr(server.client, 'write', mock_etcd_write)

        def mock_invoke_flow(flow, job):
            raise FlowExecutionFailedError("Flow Execution failed")
        monkeypatch.setattr(server, 'invoke_flow', mock_invoke_flow)

        input_raw_job1 = {
            "status": "new", "sds_type": "generic",
            "cluster_id": "49fa2adde8a6e98591f0f5cb4bc5f44d",
            "errors": {}, "attributes": {"_raw_params": "ls"},
            "type": "node",
            "message": "Executing command",
            "object_type": "generic",
            "flow": "ExecuteCommand"
        }

        pytest.raises(
            FlowExecutionFailedError,
            server._process_job,
            input_raw_job1,
            "9a9604c0-d2a6-4be0-9a82-262f10037a8f"
        )


class TestEtcdThread(object):
    def test_etcdthread_constructor(self):
        manager = SampleManager()
        user_request_thread = EtcdThread(manager)
        assert isinstance(user_request_thread._manager, SampleManager)
        assert isinstance(user_request_thread._complete, gevent.event.Event)
        assert isinstance(user_request_thread._server, EtcdRPC)

    def test_etcdthread_stop(self):
        manager = SampleManager()
        user_request_thread = EtcdThread(manager)
        assert not user_request_thread._complete.is_set()

        user_request_thread.stop()

        assert user_request_thread._complete.is_set()

    def test_etcdthread_run(self, monkeypatch):
        manager = SampleManager()
        user_request_thread = EtcdThread(manager)

        user_request_thread._complete.set()
        user_request_thread._run()

        user_request_thread2 = EtcdThread(manager)

        user_request_thread2.EXCEPTION_BACKOFF = 1

        def mock_server_run():
            raise Exception
        monkeypatch.setattr(user_request_thread._server,
                            'run', mock_server_run)

        assert True
