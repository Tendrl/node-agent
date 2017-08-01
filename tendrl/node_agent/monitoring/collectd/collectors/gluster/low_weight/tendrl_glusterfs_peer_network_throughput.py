import netifaces
import socket
import time

import tendrl_glusterfs_base


# Working Procedure:
# Find interface name from peer name(hosntname)
# 1. Read /sys/class/net/eth0/statistics/rx_bytes and
#    /sys/class/net/eth0/statistics/tx_bytes
# 2. Sleep for 1s
# 3. Repeat 1
# 4. Find diff delta rx and delta tx from 3 and 1.
# 5. Push delta rx+ delta tx to graphite

PLUGIN_NAME = 'network_throughput'
CONFIG = None


class TendrlGlusterfsNWThroughput(
    tendrl_glusterfs_base.TendrlGlusterfsMonitoringBase
):
    def __init__(self):
        tendrl_glusterfs_base.TendrlGlusterfsMonitoringBase.__init__(self)

    def get_interface_name(self, peer_name):
        infs = netifaces.interfaces()
        for inf in infs:
            if (
                netifaces.ifaddresses(inf)[2][0]['addr'] ==
                    socket.gethostbyname(peer_name)
            ):
                return inf
        return None

    def get_rx_and_tx(self, iface):
        rx = 0
        tx = 0
        with open('/sys/class/net/%s/statistics/rx_bytes' % iface, 'r') as f:
            rx = long(f.read().rstrip())
        with open('/sys/class/net/%s/statistics/tx_bytes' % iface, 'r') as f:
            tx = long(f.read().rstrip())
        return rx, tx

    def calc_network_throughput(self, peer_name):
        inf_name = self.get_interface_name(peer_name)
        if inf_name:
            rx, tx = self.get_rx_and_tx(inf_name)
            time.sleep(1)
            rx1, tx1 = self.get_rx_and_tx(inf_name)
            return (rx1 - rx) + (tx1 - tx)

    def get_metrics(self):
        ret_val = {}
        ret_val[
            'clusters.%s.nodes.%s.network_throughput-cluster_network.gauge-used' % (
                self.CONFIG['integration_id'],
                socket.getfqdn(self.CONFIG['peer_name']).replace(".", "_")
            )
        ] = self.calc_network_throughput(self.CONFIG['peer_name'])
        return ret_val
