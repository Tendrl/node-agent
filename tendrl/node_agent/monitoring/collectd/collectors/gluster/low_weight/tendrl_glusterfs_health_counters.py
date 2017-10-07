import collectd
import socket
import traceback


from tendrl_gluster import TendrlGlusterfsMonitoringBase


PEER_IN_CLUSTER = ['Peer', 'in', 'Cluster']


class TendrlGlusterfsHealthCounters(
    TendrlGlusterfsMonitoringBase
):
    def __init__(self):
        self.provisioner_only_plugin = False
        TendrlGlusterfsMonitoringBase.__init__(self)

    def _get_volume_snap_counts(self):
        ret_val = {}
        volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
        for volume in volumes:
            snap_cnt = volume.get('snap_count', 0)
            ret_val[volume['name']] = snap_cnt
        return ret_val

    def _get_vol_rebalance_bytes(self):
        ret_val = {}
        volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
        for volume in volumes:
            rebalance_data = volume.get('rebalance_data', 0)
            ret_val[volume['name']] = rebalance_data
        return ret_val

    def _get_vol_rebalance_files(self):
        ret_val = {}
        volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
        for volume in volumes:
            rebalance_files = volume.get('rebalance_files', 0)
            ret_val[volume['name']] = rebalance_files
        return ret_val

    def _get_volume_rebalance_failures(self):
        ret_val = {}
        volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
        for volume in volumes:
            rebalance_failures = volume.get('rebalance_failures', 0)
            ret_val[volume['name']] = rebalance_failures
        return ret_val

    def _get_volume_rebalance_skipped(self):
        ret_val = {}
        volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
        for volume in volumes:
            rebalance_skipped = volume.get('rebalance_skipped', 0)
            ret_val[volume['name']] = rebalance_skipped
        return ret_val

    def get_metrics(self):
        try:
            ret_val = {}
            volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
            # Push brick level connections count
            for volume in volumes:
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
            # Push volume wise snap counts
            for vol_name, snap_cnt in self._get_volume_snap_counts(
            ).iteritems():
                ret_val[
                    'clusters.%s.volumes.%s.snap_count' % (
                        self.CONFIG['integration_id'],
                        vol_name
                    )
                ] = snap_cnt
            # Push rebalance bytes progress
            for vol_name, rebalance_bytes in self._get_vol_rebalance_bytes(
            ).iteritems():
                ret_val[
                    'clusters.%s.volumes.%s.nodes.%s.rebalance_bytes' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        self.CONFIG['peer_name'].replace('.', '_')
                    )
                ] = int(filter(str.isdigit, rebalance_bytes))
            # Push rebalance files progress
            for vol_name, rebalance_files in self._get_vol_rebalance_files(
            ).iteritems():
                ret_val[
                    'clusters.%s.volumes.%s.nodes.%s.rebalance_files' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        self.CONFIG['peer_name'].replace('.', '_')
                    )
                ] = rebalance_files
            # Push rebalance failures
            for vol_name, r_failures in self._get_volume_rebalance_failures(
            ).iteritems():
                ret_val[
                    'clusters.%s.volumes.%s.nodes.%s.rebalance_failures' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        self.CONFIG['peer_name'].replace('.', '_')
                    )
                ] = r_failures
            # Push rebalance skipped
            for vol_name, r_skipped in self._get_volume_rebalance_skipped(
            ).iteritems():
                ret_val[
                    'clusters.%s.volumes.%s.nodes.%s.rebalance_skipped' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        self.CONFIG['peer_name'].replace('.', '_')
                    )
                ] = r_skipped
            return ret_val
        except (AttributeError, KeyError, ValueError):
            collectd.error(
                'Failed to fetch counters. Error %s\n\n' % (
                    traceback.format_exc()
                )
            )
            return {}
