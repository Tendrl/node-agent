import collectd
import socket
import time


# Working Procedure:
# Find interface name from peer name(hosntname)
# 1. Read /sys/class/net/eth0/statistics/rx_bytes and
#    /sys/class/net/eth0/statistics/tx_bytes
# 2. Sleep for 1s
# 3. Repeat 1
# 4. Find diff delta rx and delta tx from 3 and 1.
# 5. Push delta rx+ delta tx to graphite

PLUGIN_NAME = 'network_throughput'
CLUSTER_NETWORK = 'cluster_network'
PUBLIC_NETWORK = 'public_network'
CONFIG = None


def configure_callback(configobj):
    global CONFIG
    CONFIG = {
        c.key: c.values[0] for c in configobj.children
    }


def send_metric(
    value,
    plugin_instance=None
):
    global CONFIG
    metric = collectd.Values()
    metric.plugin = PLUGIN_NAME
    metric.host = socket.getfqdn()
    metric.type = 'gauge'
    metric.values = [value]
    metric.type_instance = 'used'
    if plugin_instance:
        metric.plugin_instance = plugin_instance
    metric.dispatch()


def get_rx_and_tx(iface):
    rx = 0
    tx = 0
    with open('/sys/class/net/%s/statistics/rx_bytes' % iface, 'r') as f:
        rx = long(f.read().rstrip())
    with open('/sys/class/net/%s/statistics/tx_bytes' % iface, 'r') as f:
        tx = long(f.read().rstrip())
    return rx, tx


def calc_network_throughput(interfaces):
    inf_throughputs = {}
    for inf_name in interfaces:
        rx, tx = get_rx_and_tx(inf_name)
        time.sleep(1)
        rx1, tx1 = get_rx_and_tx(inf_name)
        inf_throughputs[inf_name] = (rx1 - rx) + (tx1 - tx)
    return inf_throughputs


def write_throughput(interfaces, interface_type):
    node_nw_throughput = 0
    for inf_name, inf_throughput in interfaces.iteritems():
        send_metric(
            inf_throughput,
            plugin_instance=inf_name
        )
        node_nw_throughput = \
            node_nw_throughput + inf_throughput
    send_metric(
        node_nw_throughput,
        plugin_instance=interface_type
    )


def read_callback(data=None):
    global CONFIG
    write_throughput(
        calc_network_throughput(
            CONFIG[CLUSTER_NETWORK].split()
        ),
        CLUSTER_NETWORK
    )
    write_throughput(
        calc_network_throughput(
            CONFIG[PUBLIC_NETWORK].split()
        ),
        PUBLIC_NETWORK
    )


collectd.register_config(configure_callback)
collectd.register_read(read_callback, 60)
