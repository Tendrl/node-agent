import gevent
import importlib
import os
import pkgutil
import six
import traceback


import collectd


import utils as tendrl_glusterfs_utils


class PluginMount(type):

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.register_plugin(cls)

    def register_plugin(cls, plugin):
        instance = plugin()
        cls.plugins.append(instance)


@six.add_metaclass(PluginMount)
class TendrlGlusterfsMonitoringBase(gevent.greenlet.Greenlet):

    CLUSTER_TOPOLOGY = tendrl_glusterfs_utils.get_gluster_cluster_topology()
    CONFIG = {}

    def __init__(self):
        super(TendrlGlusterfsMonitoringBase, self).__init__()

    def get_metrics(self):
        pass

    def _run(self):
        metrics = self.get_metrics()
        gevent.sleep(0.1)
        for metric_name, value in metrics.iteritems():
            try:
                gevent.sleep(0.1)
                if value is not None:
                    if (
                        isinstance(value, str) and
                        value.isdigit()
                    ):
                        value = int(value)
                    gevent.sleep(0.1)
                    tendrl_glusterfs_utils.write_graphite(
                        metric_name,
                        value,
                        self.CONFIG['graphite_host'],
                        self.CONFIG['graphite_port']
                    )
            except Exception:
                collectd.error(
                    'Exception trying to fetch push stats. Error %s\n\n' % (
                        traceback.format_exc()
                    )
                )


def list_modules_in_package_path(package_path, prefix):
    modules = []
    path_to_walk = [(package_path, prefix)]
    while len(path_to_walk) > 0:
        curr_path, curr_prefix = path_to_walk.pop()
        for importer, name, ispkg in pkgutil.walk_packages(
            path=[curr_path]
        ):
            if ispkg:
                path_to_walk.append(
                    (
                        '%s/%s/' % (curr_path, name),
                        '%s.%s' % (curr_prefix, name)
                    )
                )
            else:
                modules.append((name, '%s.%s' % (curr_prefix, name)))
    return modules


def load_plugins():
    path = os.path.dirname(os.path.abspath(__file__)) + '/low_weight'
    pkg = 'low_weight'
    sds_plugins = list_modules_in_package_path(path, pkg)
    for name, sds_fqdn in sds_plugins:
        importlib.import_module(sds_fqdn)


def read_callback():
    load_plugins()
    for gfsmon_plugin in TendrlGlusterfsMonitoringBase.plugins:
        gevent.sleep(0.1)
        gfsmon_plugin.start()


def configure_callback(configobj):
    TendrlGlusterfsMonitoringBase.CONFIG = {
        c.key: c.values[0] for c in configobj.children
    }


collectd.register_config(configure_callback)
collectd.register_read(read_callback, 60)
