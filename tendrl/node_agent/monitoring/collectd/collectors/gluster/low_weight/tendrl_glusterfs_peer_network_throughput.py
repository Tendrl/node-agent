import collectd
import netifaces
import socket
import sys
import time

sys.path.append('/usr/lib64/collectd/gluster')
import utils as tendrl_glusterfs_utils
sys.path.remove('/usr/lib64/collectd/gluster')


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


def get_iface_stats(iface):
    iface_stats = {
        'if_collisions': None,
        'if_multicast': None,
        'if_bytes': {
            'rx': None,
            'tx': None
        },
        'if_compressed': {
            'rx': None,
            'tx': None
        },
        'if_dropped': {
            'rx': None,
            'tx': None
        },
        'if_errors': {
            'rx': None,
            'tx': None
        },
        'if_fifo_errors': {
            'rx': None,
            'tx': None
        },
        'if_over_errors': {
            'rx': None
        },
        'if_packets': {
            'rx': None,
            'tx': None
        }
    }
    if not iface:
        return iface_stats
    with open('/sys/class/net/%s/statistics/rx_bytes' % iface, 'r') as f:
        iface_stats['if_bytes']['rx'] = long(f.read().rstrip())
    with open('/sys/class/net/%s/statistics/tx_bytes' % iface, 'r') as f:
        iface_stats['if_bytes']['tx'] = long(f.read().rstrip())
    with open('/sys/class/net/%s/statistics/rx_compressed' % iface, 'r') as f:
        iface_stats['if_compressed']['rx'] = long(f.read().rstrip())
    with open('/sys/class/net/%s/statistics/tx_compressed' % iface, 'r') as f:
        iface_stats['if_compressed']['tx'] = long(f.read().rstrip())
    with open('/sys/class/net/%s/statistics/rx_dropped' % iface, 'r') as f:
        iface_stats['if_dropped']['rx'] = long(f.read().rstrip())
    with open('/sys/class/net/%s/statistics/tx_dropped' % iface, 'r') as f:
        iface_stats['if_dropped']['tx'] = long(f.read().rstrip())
    with open('/sys/class/net/%s/statistics/rx_errors' % iface, 'r') as f:
        iface_stats['if_errors']['rx'] = long(f.read().rstrip())
    with open('/sys/class/net/%s/statistics/tx_errors' % iface, 'r') as f:
        iface_stats['if_errors']['tx'] = long(f.read().rstrip())
    with open('/sys/class/net/%s/statistics/rx_fifo_errors' % iface, 'r') as f:
        iface_stats['if_fifo_errors']['rx'] = long(f.read().rstrip())
    with open('/sys/class/net/%s/statistics/tx_fifo_errors' % iface, 'r') as f:
        iface_stats['if_fifo_errors']['tx'] = long(f.read().rstrip())
    with open('/sys/class/net/%s/statistics/rx_over_errors' % iface, 'r') as f:
        iface_stats['if_over_errors']['rx'] = long(f.read().rstrip())
    with open('/sys/class/net/%s/statistics/rx_packets' % iface, 'r') as f:
        iface_stats['if_packets']['rx'] = long(f.read().rstrip())
    with open('/sys/class/net/%s/statistics/tx_packets' % iface, 'r') as f:
        iface_stats['if_packets']['tx'] = long(f.read().rstrip())
    return iface_stats


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
    global CONFIG
    ret_val = {}
    t_name = 'clusters.%s.nodes.%s.network_throughput-cluster_network.' \
        'gauge-used'
    ret_val[
        t_name % (
            CONFIG['integration_id'],
            socket.getfqdn(CONFIG['peer_name']).replace(".", "_")
        )
    ] = calc_network_throughput(CONFIG['peer_name'])
    nw_stats = get_iface_stats(
        get_interface_name(CONFIG['peer_name'])
    )
    t_name = 'clusters.%s.nodes.%s.cluster_network.%s'
    for if_stat_type, val in nw_stats.iteritems():
        if isinstance(val, dict):
            for stat_type, stat_val in val.iteritems():
                if_stat_name = "%s.%s" % (if_stat_type, stat_type)
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        CONFIG['peer_name'].replace(".", "_"),
                        if_stat_name
                    )
                ] = stat_val
        else:
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    CONFIG['peer_name'].replace(".", "_"),
                    if_stat_type
                )
            ] = val
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
