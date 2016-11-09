import gevent.event
from mock import MagicMock
import sys
sys.modules['tendrl.node_agent.config'] = MagicMock()
sys.modules['tendrl.bridge_common.log'] = MagicMock()

from tendrl.node_agent.manager.manager import Manager
from tendrl.node_agent.manager.rpc import EtcdThread
del sys.modules['tendrl.node_agent.config']


class TestManager(object):
    def test_manager_constructor(self):
        manager = Manager()
        assert isinstance(manager._user_request_thread, EtcdThread)
        assert isinstance(manager._complete, gevent.event.Event)

    def test_manager_stop(self, monkeypatch):
        manager = Manager()

        def mock_user_request_thread_stop():
            return
        monkeypatch.setattr(manager._user_request_thread,
                            'stop',
                            mock_user_request_thread_stop)

        def mock_discovery_thread_stop():
            return
        monkeypatch.setattr(manager._discovery_thread,
                            'stop',
                            mock_discovery_thread_stop)

        def mock_persister_stop():
            return
        monkeypatch.setattr(manager.persister,
                            'stop',
                            mock_persister_stop)

        manager.stop()
        assert True

    def test_manager_start(self, monkeypatch):
        manager = Manager()

        def mock_user_request_thread_start():
            return
        monkeypatch.setattr(manager._user_request_thread,
                            'start',
                            mock_user_request_thread_start)

        def mock_discovery_thread_start():
            return
        monkeypatch.setattr(manager._discovery_thread,
                            'start',
                            mock_discovery_thread_start)

        def mock_persister_start():
            return
        monkeypatch.setattr(manager.persister,
                            'start',
                            mock_persister_start)

        manager.start()
        assert True

    def test_manager_join(self, monkeypatch):
        manager = Manager()

        def mock_user_request_thread_join():
            return
        monkeypatch.setattr(manager._user_request_thread,
                            'join',
                            mock_user_request_thread_join)

        def mock_discovery_thread_join():
            return
        monkeypatch.setattr(manager._discovery_thread,
                            'join',
                            mock_discovery_thread_join)

        def mock_persister_join():
            return
        monkeypatch.setattr(manager.persister,
                            'join',
                            mock_persister_join)

        manager.join()
        assert True
