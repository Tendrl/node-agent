import importlib
import os
import pkgutil
import six
import sys
import threading
import time


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
    """The collectd plugin base class.

    Extend it to:

    1. Automatically have a custom plugin execute & push stats to time

       series db.

    2. Readily get the cluster topology obtained by this base framework parsing

       gluster get-state glusterd o/p

    Rules for choosing plugin path are as follows:

    a. Plugins under /usr/lib64/collectd/gluster/low_weight that extend base

       class TendrlGlusterfsMonitoringBase automatically run every:

       base node_agent sync interval + 77 s

    b. Plugins under /usr/lib64/collectd/gluster/heavy_weight that extend base

       class TendrlGlusterfsMonitoringBase automatically run every:

       base node_agent sync interval + 77 + 37 s.

        i. The plugins here are called provisioner_only_plugin and are executed

           only on node marked as provisioner in collectd configuration file.
    """
    CLUSTER_TOPOLOGY = {}
    CONFIG = {}

    def __init__(self):
        super(TendrlGlusterfsMonitoringBase, self).__init__()

    def get_metrics(self):
        """Extend this method in the collectd plugin and add logic to fetch

        metrics and return the metrics from this function.

        Args: None

        Returns: List of metrics where metrics is dict of type:

                {graphite_series_name:value}
        """
        pass

    def run(self):
        """The default run function that is responsible for:

        1. Get stats from get_metrics of the plugin and push to time-series

           db after value validations(only non nul validation

           for now).

        2. Add latency to provisioner_only_plugin(heavy_weight plugins)
        """
        # If provisioner_only_plugin(plugins that can cause costly sds
        # locking issues) add additional latency of 37 s to execution of
        # such plugins
        if self.provisioner_only_plugin:
            time.sleep(13)
        # Get stats from current plugin's get_metrics function
        metrics = self.get_metrics()
        metric_list = []
        for metric_name, value in metrics.iteritems():
            # Don't push null values to graphite
            if value is not None:
                if (
                    isinstance(value, str) and
                    value.isdigit()
                ):
                    value = int(value)
                metric_list.append("tendrl.%s %s %d" % (
                    metric_name,
                    value,
                    int(time.time())
                ))
        # Push value to graphite
        tendrl_glusterfs_utils.write_graphite(
            metric_list,
            self.CONFIG['graphite_host'],
            self.CONFIG['graphite_port']
        )


def list_modules_in_package_path(package_path, prefix):
    """Get the list of all modules in required package_path recursively

    Args:

        package_path: The fully qualified linux path of the python package

                      to traverse recursively

        prefix: The root python package name for the plugins

    Returns: List of modules in the given package path.
    """
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
    """This does the following:

    1. Get list of plugins(modules) in the required package path

    2. Import the plugins(modules).

    When the plugins are imported, class PluginMount marked as metaclass

    (as in base class "TendrlGlusterfsMonitoringBase" definition)for the

    plugins, register the current imported plugin into a class variable

    called "plugins" and hereafter, TendrlGlusterfsMonitoringBase.plugins

    gives the list of all tendrl recognised collectd plugins(in other

    words the plugins that extend TendrlGlusterfsMonitoringBase)

    Args:

        pkg_path: The fully qualified linux path of the python package

                      to traverse recursively

        pkg: The root python package name for the plugins
    """
    path = os.path.dirname(os.path.abspath(__file__)) + pkg_path
    sds_plugins = list_modules_in_package_path(path, pkg)
    for name, sds_fqdn in sds_plugins:
        if sds_fqdn in sys.modules:
            # Reload module if hot fixes need to be auto-picked in next cycle
            reload(sys.modules[sds_fqdn])
            # continue
        else:
            importlib.import_module(sds_fqdn)


threads = []


def get_exisiting_thread(thread_name):
    """Get thread by name

    Args:

        thread_name: Name of the thread. Usually the plugin name.

    Returns:

        thread if there exists one with same name already otherwise null
    """
    global threads
    for thread in threads:
        if thread.name == thread_name:
            return thread
    return None


def read_callback(pkg_path, pkg):
    global threads
    load_plugins(pkg_path, pkg)
    for gfsmon_plugin in TendrlGlusterfsMonitoringBase.plugins:
        # If the plugin is marked as provisioner_only_plugin(heavy-weight)
        # Execute such a plugin only on the current node if and only if the
        # the current node is marked as provisioner in collectd's conf file.
        if gfsmon_plugin.provisioner_only_plugin:
            if (
                not TendrlGlusterfsMonitoringBase.CONFIG['provisioner'] or
                TendrlGlusterfsMonitoringBase.CONFIG[
                    'provisioner'
                ] == "False"
            ):
                continue
        # Check if a thread by name same as the name of plugin exists.
        thread = get_exisiting_thread(
            gfsmon_plugin.__class__.__name__
        )
        if not thread:
            # If it does not exist, spawn a thread for plugin execution and set
            # its name to name of the plugin
            thread = threading.Thread(
                target=gfsmon_plugin.run,
                args=()
            )
            thread.setName(gfsmon_plugin.__class__.__name__)
            threads.append(
                thread
            )
    # Statr the threads and wait till all of them exit.
    for index in range(len(threads)):
        threads[index].start()
        threads[index].join(1)
    # Cleanup the threads
    for index in range(len(threads)):
        del threads[0]


def init():
    TendrlGlusterfsMonitoringBase.CLUSTER_TOPOLOGY = \
        tendrl_glusterfs_utils.get_gluster_cluster_topology()


def destroy():
    """Destroy the plugin states and threads"""
    global threads
    for index in range(len(TendrlGlusterfsMonitoringBase.plugins)):
        del TendrlGlusterfsMonitoringBase.plugins[0]
    while len(threads) != 0:
        continue


def r_callback():
    """Function registered to collectd as to be invoked for stats collection

    and hence will be executed at every:

        read interval of 77s + node_agent sync interval

    Destroy the plugin threads after execution
    """
    init()
    read_callback("/low_weight", "low_weight")
    read_callback("/heavy_weight", "heavy_weight")
    destroy()


def configure_callback(configobj):
    """Function registered to collectd for parsing collectd configuration.

    The configuration is maintained in a global variable.

    Args:

        configobj: The collectd passed configuration tree parsed from collectd

                   config file
    """
    TendrlGlusterfsMonitoringBase.CONFIG = {
        c.key: c.values[0] for c in configobj.children
    }


collectd.register_config(configure_callback)
collectd.register_read(r_callback, 77)
