import importlib
import os
import pkgutil
import six
import threading
import time


import blivet
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
class TendrlGlusterfsMonitoringBase(object):

    CLUSTER_TOPOLOGY = tendrl_glusterfs_utils.get_gluster_cluster_topology()
    CONFIG = {}
    b = blivet.Blivet()
    b.reset()
    DEVICE_TREE = b.devicetree

    def __init__(self):
        super(TendrlGlusterfsMonitoringBase, self).__init__()

    def get_metrics(self):
        pass

    def run(self):
        if self.provisioner_only_plugin:
            time.sleep(37)
        metrics = self.get_metrics()
        for metric_name, value in metrics.iteritems():
            if value is not None:
                if (
                    isinstance(value, str) and
                    value.isdigit()
                ):
                    value = int(value)
                tendrl_glusterfs_utils.write_graphite(
                    metric_name,
                    value,
                    self.CONFIG['graphite_host'],
                    self.CONFIG['graphite_port']
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


def load_plugins(pkg_path, pkg):
    path = os.path.dirname(os.path.abspath(__file__)) + pkg_path
    sds_plugins = list_modules_in_package_path(path, pkg)
    for name, sds_fqdn in sds_plugins:
        importlib.import_module(sds_fqdn)


threads = []


def get_exisiting_thread(thread_name):
    global threads
    for thread in threads:
        if thread.name == thread_name:
            return thread
    return None


def read_callback(pkg_path, pkg):
    global threads
    load_plugins(pkg_path, pkg)
    for gfsmon_plugin in TendrlGlusterfsMonitoringBase.plugins:
        if gfsmon_plugin.provisioner_only_plugin:
            if (
                not TendrlGlusterfsMonitoringBase.CONFIG['provisioner'] or
                TendrlGlusterfsMonitoringBase.CONFIG[
                    'provisioner'
                ] == "False"
            ):
                continue
        thread = get_exisiting_thread(
            gfsmon_plugin.__class__.__name__
        )
        if not thread:
            thread = threading.Thread(
                target=gfsmon_plugin.run,
                args=()
            )
            thread.setName(gfsmon_plugin.__class__.__name__)
            threads.append(
                thread
            )
    for index in range(len(threads)):
        threads[index].start()
        threads[index].join(1)
    for index in range(len(threads)):
        del threads[0]


def r_callback():
    read_callback("/low_weight", "low_weight")
    read_callback("/heavy_weight", "heavy_weight")


def configure_callback(configobj):
    TendrlGlusterfsMonitoringBase.CONFIG = {
        c.key: c.values[0] for c in configobj.children
    }


collectd.register_config(configure_callback)
collectd.register_read(r_callback, 77)
