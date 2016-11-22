import gevent.event
from mock import MagicMock
import os
import shutil
import sys
import tempfile
sys.modules['tendrl.node_agent.persistence.persister'] = MagicMock()
sys.modules['tendrl.node_agent.config'] = MagicMock()
sys.modules['tendrl.common.log'] = MagicMock()
from tendrl.node_agent.manager import manager
from tendrl.node_agent.manager.rpc import EtcdThread
del sys.modules['tendrl.node_agent.persistence.persister']
del sys.modules['tendrl.common.log']
del sys.modules['tendrl.node_agent.config']


class TestManager(object):
    def setup_method(self, method):
        manager.pull_hardware_inventory = MagicMock()
        manager.utils = MagicMock()
        self.manager = manager.Manager(
            'aa22a6fe-87f0-45cf-8b70-2d0ff4c02af6')

    def test_manager_constructor(self):
        assert isinstance(self.manager._user_request_thread, EtcdThread)
        assert isinstance(self.manager._complete, gevent.event.Event)
        assert isinstance(
            self.manager._discovery_thread, manager.TopLevelEvents)

    def test_register_node(self):
        self.manager.persister.update_node_context.assert_called()
        self.manager.persister.update_node_context.assert_called()
        self.manager.persister.update_tendrl_definitions.assert_called()

    def test_manager_stop(self, monkeypatch):

        def mock_user_request_thread_stop():
            return
        monkeypatch.setattr(self.manager._user_request_thread,
                            'stop',
                            mock_user_request_thread_stop)

        def mock_discovery_thread_stop():
            return
        monkeypatch.setattr(self.manager._discovery_thread,
                            'stop',
                            mock_discovery_thread_stop)

        def mock_persister_stop():
            return
        monkeypatch.setattr(self.manager.persister,
                            'stop',
                            mock_persister_stop)

        self.manager.stop()
        assert True

    def test_manager_start(self, monkeypatch):

        def mock_user_request_thread_start():
            return
        monkeypatch.setattr(self.manager._user_request_thread,
                            'start',
                            mock_user_request_thread_start)

        def mock_discovery_thread_start():
            return
        monkeypatch.setattr(self.manager._discovery_thread,
                            'start',
                            mock_discovery_thread_start)

        def mock_persister_start():
            return
        monkeypatch.setattr(self.manager.persister,
                            'start',
                            mock_persister_start)

        self.manager.start()
        assert True

    def test_manager_join(self, monkeypatch):

        def mock_user_request_thread_join():
            return
        monkeypatch.setattr(self.manager._user_request_thread,
                            'join',
                            mock_user_request_thread_join)

        def mock_discovery_thread_join():
            return
        monkeypatch.setattr(self.manager._discovery_thread,
                            'join',
                            mock_discovery_thread_join)

        def mock_persister_join():
            return
        monkeypatch.setattr(self.manager.persister,
                            'join',
                            mock_persister_join)

        self.manager.join()
        assert True


class TestTopLevelEvents(object):
    def setup_method(self, method):
        manager.gevent = MagicMock()
        manager.json = MagicMock()
        self.manager = manager.Manager('aa22a6fe-87f0-45cf-8b70-2d0ff4c02af6')
        self.TopLevelEvents = manager.TopLevelEvents(self.manager)
        self.ret = True

    def test_run(self, monkeypatch):
        node_inventory = (
            {
                "node_id": "0e4f5489-4cc3-4264-84be-b4fc9a6259e7",
                "memory": {"TotalSize": "1016188 kB",
                           "SwapTotal": "0 kB"
                           },
                "machine_id": "0a9f65533cdf4cf2abc4b8ba7f7b2aba",
                "os": {"KernelVersion": "3.10.0-123.el7.x86_64",
                       "SELinuxMode": "Enforcing",
                       "OSVersion": "7.0.1406",
                       "Name": "CentOS Linux",
                       "FQDN": "dhcp41-152.lab.eng.blr.redhat.com"
                       },
                "cpu": {"Model": "42",
                        "VendorId": "GenuineIntel",
                        "ModelName": "Intel Xeon E312xx (Sandy Bridge)",
                        "Architecture": "x86_64",
                        "CoresPerSocket": "1",
                        "CpuOpMode": "32-bit, 64-bit",
                        "CPUFamily": "6",
                        "CPUs": "1"
                        },
                "tendrl_context": {"sds_version": "10.2.3",
                                   "sds_name": "ceph"
                                   }
            })
        manager.pull_hardware_inventory.get_node_inventory = \
            MagicMock(return_value=node_inventory)
        self.tempdir = tempfile.mkdtemp()
        manager.HARDWARE_INVENTORY_FILE = os.path.join(self.tempdir, "temp")
        self.TopLevelEvents._complete = self
        self.TopLevelEvents._run()
        self.manager.persister.update_node_context.assert_called()
        self.manager.persister.update_node.assert_called()
        self.manager.persister.update_tendrl_context.assert_called()
        self.manager.persister.update_os.assert_called()
        self.manager.persister.update_memory.assert_called()
        self.manager.persister.update_cpu.assert_called()

    def is_set(self):
        self.ret = not self.ret
        return self.ret

    def teardown_method(self, method):
        shutil.rmtree(self.tempdir)
