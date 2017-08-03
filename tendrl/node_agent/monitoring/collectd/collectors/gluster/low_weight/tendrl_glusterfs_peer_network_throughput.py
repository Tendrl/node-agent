import collectd
import netifaces
import socket
import time
import traceback

import utils as tendrl_glusterfs_utils


# Working Procedure:
# Find interface name from peer name(hosntname)
# 1. Read /sys/class/net/eth0/statistics/rx_bytes and
#    /sys/class/net/eth0/statistics/tx_bytes
# 2. Sleep for 1s
# 3. Repeat 1
# 4. Find diff delta rx and delta tx from 3 and 1.
# 5. Push delta rx+ delta tx to graphite

PLUGIN_NAME = 'network_throughput'
CONFIG = {}
CLUSTER_TOPOLOGY = {}


def get_interface_name(peer_name):
    infs = netifaces.interfaces()
    for inf in infs:
        if (
            netifaces.ifaddresses(inf)[2][0]['addr'] ==
                socket.gethostbyname(peer_name)
        ):
            return inf
    return None


def get_rx_and_tx(iface):
    rx = 0
    tx = 0
    with open('/sys/class/net/%s/statistics/rx_bytes' % iface, 'r') as f:
        rx = long(f.read().rstrip())
    with open('/sys/class/net/%s/statistics/tx_bytes' % iface, 'r') as f:
        tx = long(f.read().rstrip())
    return rx, tx


def calc_network_throughput(peer_name):
    inf_name = get_interface_name(peer_name)
    if inf_name:
        rx, tx = get_rx_and_tx(inf_name)
        time.sleep(1)
        rx1, tx1 = get_rx_and_tx(inf_name)
        return (rx1 - rx) + (tx1 - tx)


def get_metrics():
    ret_val = {}
    t_name = 'clusters.%s.nodes.%s.network_throughput-cluster_network.' \
        'gauge-used'
    ret_val[
        t_name % (
            CONFIG['integration_id'],
            socket.getfqdn(CONFIG['peer_name']).replace(".", "_")
        )
    ] = calc_network_throughput(CONFIG['peer_name'])
    return ret_val


def read_callback():
    global CLUSTER_TOPOLOGY
    global CONFIG
    CLUSTER_TOPOLOGY = \
        tendrl_glusterfs_utils.get_gluster_cluster_topology()
    metrics = get_metrics()
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
                CONFIG['graphite_host'],
                CONFIG['graphite_port']
            )


def configure_callback(configobj):
    global CONFIG
    CONFIG = {
        c.key: c.values[0] for c in configobj.children
    }


collectd.register_config(configure_callback)
collectd.register_read(read_callback, 60)
