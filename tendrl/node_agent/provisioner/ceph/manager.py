import importlib
import inspect
import logging
import os
import re

from tendrl.node_agent.provisioner.ceph import provisioner_base

LOG = logging.getLogger(__name__)


class ProvisioningManager(object):

    def __init__(self, provisioner):
        self.ceph_provisioner = provisioner
        try:
            self.load_plugins()
        except (SyntaxError, ValueError, ImportError) as ex:
            raise ex
        self.plugin = None
        self.set_plugin()

    def load_plugins(self):
        try:
            path = os.path.dirname(os.path.abspath(__file__)) + '/plugins'
            pkg = 'tendrl.node_agent.provisioner.ceph.plugins'
            for py in [f[:-3] for f in os.listdir(path)
                       if f.endswith('.py') and f != '__init__.py']:
                plugin_name = '.'.join([pkg, py])
                mod = importlib.import_module(plugin_name)
                clsmembers = inspect.getmembers(mod, inspect.isclass)
                for name, cls in clsmembers:
                    exec("from %s import %s" % (plugin_name, name))
        except (SyntaxError, ValueError, ImportError) as ex:
            LOG.error('Failed to load the ceph provisioner plugins. Error %s' %
                      ex, exc_info=True)
            raise ex

    def get_plugin(self):
        return self.plugin

    def set_plugin(self):
        for plugin in provisioner_base.ProvisionerBasePlugin.plugins:
            if re.search(self.ceph_provisioner.lower(), type(
                    plugin).__name__.lower(), re.IGNORECASE):
                self.plugin = plugin

    def stop(self):
        self.plugin.destroy()
