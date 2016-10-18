import gevent.event
from tendrl.node_agent.manager.manager import Manager
from tendrl.node_agent.manager.rpc import EtcdThread


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
        manager.stop()
        assert True

    def test_manager_recover(self):
        manager = Manager()
        manager._recover()
        assert True

    def test_manager_start(self, monkeypatch):
        manager = Manager()

        def mock_user_request_thread_start():
            return
        monkeypatch.setattr(manager._user_request_thread,
                            'start',
                            mock_user_request_thread_start)
        manager.start()
        assert True

    def test_manager_join(self, monkeypatch):
        manager = Manager()

        def mock_user_request_thread_join():
            return
        monkeypatch.setattr(manager._user_request_thread,
                            'join',
                            mock_user_request_thread_join)
        manager.join()
        assert True
