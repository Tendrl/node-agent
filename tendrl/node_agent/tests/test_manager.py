import maps
import mock
import threading

from tendrl.node_agent import manager
from tendrl.node_agent.manager import \
    NodeAgentManager
from tendrl.node_agent.objects.config import \
    Config
from tendrl.node_agent.objects.definition import \
    Definition
from tendrl.node_agent.tests.test_init import init


class TestNodeAgent_manager(object):
    def setup_method(self, method):
        init()

    @mock.patch(
        'tendrl.node_agent.discovery.platform.manager.'
        'PlatformManager.__init__',
        mock.Mock(return_value=None)
    )
    @mock.patch(
        'tendrl.node_agent.discovery.platform.manager.'
        'PlatformManager.get_available_plugins',
        mock.Mock(return_value="test-plugin")
    )
    @mock.patch(
        'tendrl.node_agent.discovery.platform.base.'
        'PlatformDiscoverPlugin.discover_platform',
        mock.Mock(return_value={})
    )
    def test_constructor(monkeypatch):
        """Test for constructor involves if all the needed

        variables are initialized
        """

        setattr(NS, "node_agent", maps.NamedDict())
        setattr(NS, "publisher_id", "node_agent")
        manager = NodeAgentManager()
        assert isinstance(manager._message_handler_thread, mock.MagicMock)

    @mock.patch(
        'tendrl.node_agent.manager.NodeAgentManager.start',
        mock.Mock()
    )
    @mock.patch(
        'tendrl.node_agent.manager.NodeAgentManager.stop',
        mock.Mock()
    )
    @mock.patch(
        'threading.Event', mock.Mock(return_value=threading.Event())
    )
    @mock.patch(
        'tendrl.node_agent.NodeAgentNS.__init__',
        mock.Mock(return_value=None)
    )
    @mock.patch(
        'tendrl.commons.TendrlNS.__init__',
        mock.Mock(return_value=None)
    )
    @mock.patch(
        'tendrl.commons.message.Message.__init__',
        mock.Mock(return_value=None)
    )
    @mock.patch(
        'tendrl.commons.utils.log_utils.log',
        mock.Mock(return_value=None)
    )
    @mock.patch(
        'tendrl.node_agent.objects.definition.Definition.save',
        mock.Mock(return_value=None)
    )
    @mock.patch(
        'tendrl.node_agent.objects.config.Config.save',
        mock.Mock(return_value=None)
    )
    @mock.patch(
        'tendrl.node_agent.objects.definition.Definition.__init__',
        mock.Mock(return_value=None)
    )
    @mock.patch(
        'tendrl.node_agent.objects.config.Config.__init__',
        mock.Mock(return_value=None)
    )
    @mock.patch(
        'tendrl.node_agent.node_sync'
        '.NodeAgentSyncThread.__init__',
        mock.Mock(return_value=None)
    )
    @mock.patch(
        'tendrl.node_agent.message'
        '.handler.MessageHandler.__init__',
        mock.Mock(return_value=None)
    )
    @mock.patch(
        'signal.signal', mock.Mock(return_value=None)
    )
    def test_main(monkeypatch):
        NS.tendrl_context = mock.MagicMock()
        NS.message_handler_thread = mock.MagicMock()

        defs = Definition()
        defs.data = mock.MagicMock()
        cfgs = Config()
        cfgs.data = {"with_internal_profiling": False}
        setattr(NS, "node_agent", maps.NamedDict())
        setattr(NS, "type", "node")
        setattr(NS, "publisher_id", "node_agent")
        NS.node_agent.definitions = defs
        NS.node_agent.config = cfgs

        t = threading.Thread(target=manager.main, kwargs={})
        t.start()
        t.join()

        assert NS.message_handler_thread is not None

        with mock.patch.object(NodeAgentManager, 'start') \
            as manager_start:
            manager_start.assert_called
        with mock.patch.object(Definition, 'save') as def_save:
            def_save.assert_called
        with mock.patch.object(Config, 'save') as conf_save:
            conf_save.assert_called
