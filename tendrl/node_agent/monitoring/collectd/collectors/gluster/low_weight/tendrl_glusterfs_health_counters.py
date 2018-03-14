import collectd
import socket
import traceback

import utils as tendrl_glusterfs_utils


from tendrl_gluster import TendrlGlusterfsMonitoringBase


PEER_IN_CLUSTER = ['Peer', 'in', 'Cluster']


class TendrlGlusterfsHealthCounters(
    TendrlGlusterfsMonitoringBase
):
    def __init__(self):
        self.provisioner_only_plugin = False
        TendrlGlusterfsMonitoringBase.__init__(self)

    def _get_rebalance_info(self):
        ret_val = {}
        volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
        for volume in volumes:
            ret_val[volume['name']] = {}
            # snap counts
            ret_val[volume['name']]['snap_count'] = \
                volume.get('snap_count', 0)
            # rebalance_data
            rebalance_data = volume.get('rebalance_data', 0)
            ret_val[volume['name']]['rebalance_data'] = \
                tendrl_glusterfs_utils.get_size_MB(rebalance_data)
            # rebalance_files
            ret_val[volume['name']]['rebalance_files'] = \
                volume.get('rebalance_files', 0)
            # rebalance_failures
            ret_val[volume['name']]['rebalance_failures'] = \
                volume.get('rebalance_failures', 0)
            # rebalance_skipped
            ret_val[volume['name']]['rebalance_skipped'] = \
                volume.get('rebalance_skipped', 0)
        return ret_val

    def get_metrics(self):
        try:
            ret_val = {}
            volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
            # Push brick level connections count
            volumes_list = []
            for volume in volumes:
                brick_found_for_curr_node = False
                for sub_volume_index, sub_volume_bricks in volume.get(
                    'bricks',
                    {}
                ).iteritems():
                    for brick in sub_volume_bricks:
                        brick_hostname = brick.get('hostname')
                        if (
                            brick_hostname == socket.gethostbyname(
                                self.CONFIG['peer_name']
                            ) or
                            brick_hostname == self.CONFIG['peer_name']
                        ):
                            brick_found_for_curr_node = True
                            # Push brick client connections
                            ret_val[
                                'clusters.%s.volumes.%s.nodes.%s.bricks.%s.'
                                'connections_count' % (
                                    self.CONFIG['integration_id'],
                                    volume.get('name', ''),
                                    self.CONFIG['peer_name'].replace('.', '_'),
                                    brick['path'].replace('/', '|')
                                )
                            ] = brick['connections_count']
                if brick_found_for_curr_node:
                    # Update rebalance info only for this volumes
                    volumes_list.append(volume.get('name', ''))
            # push rebalance info
            rebalance_info = self._get_rebalance_info()
            for vol_name in rebalance_info:
                if vol_name in volumes_list:
                    # Push volume wise snap counts
                    ret_val[
                        'clusters.%s.volumes.%s.snap_count' % (
                            self.CONFIG['integration_id'],
                            vol_name
                        )
                    ] = rebalance_info[vol_name]['snap_count']
                    # Push rebalance bytes progress
                    ret_val[
                        'clusters.%s.volumes.%s.nodes.%s.rebalance_bytes' % (
                            self.CONFIG['integration_id'],
                            vol_name,
                            self.CONFIG['peer_name'].replace('.', '_')
                        )
                    ] = rebalance_info[vol_name]['rebalance_data']
                    # Push rebalance files progress
                    ret_val[
                        'clusters.%s.volumes.%s.nodes.%s.rebalance_files' % (
                            self.CONFIG['integration_id'],
                            vol_name,
                            self.CONFIG['peer_name'].replace('.', '_')
                        )
                    ] = rebalance_info[vol_name]['rebalance_files']
                    # Push rebalance failures
                    ret_val[
                        'clusters.%s.volumes.%s.nodes.%s.'
                        'rebalance_failures' % (
                            self.CONFIG['integration_id'],
                            vol_name,
                            self.CONFIG['peer_name'].replace('.', '_')
                        )
                    ] = rebalance_info[vol_name]['rebalance_failures']
                    # Push rebalance skipped
                    ret_val[
                        'clusters.%s.volumes.%s.nodes.%s.rebalance_skipped' % (
                            self.CONFIG['integration_id'],
                            vol_name,
                            self.CONFIG['peer_name'].replace('.', '_')
                        )
                    ] = rebalance_info[vol_name]['rebalance_skipped']
            return ret_val
        except (AttributeError, KeyError, ValueError):
            collectd.error(
                'Failed to fetch counters. Error %s\n\n' % (
                    traceback.format_exc()
                )
            )
            return {}
