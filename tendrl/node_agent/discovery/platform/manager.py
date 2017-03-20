import importlib
import inspect
import logging
import os

from tendrl.node_agent.discovery.platform import base


LOG = logging.getLogger(__name__)


class PlatformManager(object):

    def __init__(self):
        try:
            self.load_plugins()
        except (SyntaxError, ValueError, ImportError) as ex:
            raise ValueError('PlatformManager init failed %s' % ex)

    def load_plugins(self):
        try:

            path = os.path.dirname(os.path.abspath(__file__)) + '/plugins'
            pkg = 'tendrl.node_agent.discovery.platform.plugins'
            for py in [f[:-3] for f in os.listdir(path)
                       if f.endswith('.py') and f != '__init__.py']:
                plugin_name = '.'.join([pkg, py])
                mod = importlib.import_module(plugin_name)
                clsmembers = inspect.getmembers(mod, inspect.isclass)
                for name, cls in clsmembers:
                    exec("from %s import %s" % (plugin_name, name))
        except (SyntaxError, ValueError, ImportError) as ex:
            LOG.error('Failed to load the platform plugins. Error %s', ex,
                      exc_info=True)
            raise ex
        return

    def get_available_plugins(self):
        return base.PlatformDiscoverPlugin.plugins
