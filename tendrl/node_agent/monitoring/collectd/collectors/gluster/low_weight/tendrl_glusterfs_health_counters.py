import collectd
import socket
import traceback


from tendrl_gluster import TendrlGlusterfsMonitoringBase
import utils as gluster_utils


PEER_IN_CLUSTER = ['Peer', 'in', 'Cluster']


class TendrlGlusterfsHealthCounters(
    TendrlGlusterfsMonitoringBase
):
    def __init__(self):
        self.provisioner_only_plugin = False
        TendrlGlusterfsMonitoringBase.__init__(self)

    def _get_peer_count(self):
        global PEER_IN_CLUSTER
        peer_down_cnt = 0
        peers = self.CLUSTER_TOPOLOGY.get('peers', [])
        # Peer list in get-state output doesn't provide info of current node
        peer_total_cnt = len(peers) + 1
        # To test: What if current node glusterd is down ?? or peer is out of
        # cluster for any reason..
        for peer in peers:
            if (
                not (peer['connected'] == 'Connected') or
                not (
                    len(
                        set(peer['state']) & set(
                            PEER_IN_CLUSTER
                        )
                    ) == len(
                        PEER_IN_CLUSTER
                    )
                )
            ):
                peer_down_cnt = peer_down_cnt + 1
        return (
            peer_total_cnt,
            peer_down_cnt,
            peer_total_cnt - peer_down_cnt
        )

    def _get_volume_statuses(self):
        ret_val = {}
        volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
        for volume in volumes:
            status = volume.get('status', '')
            ret_val[volume['name']] = \
                gluster_utils.get_volume_state_mapping(status)
        return ret_val

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

    def _get_volume_status_wise_counts(self):
        volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
        volume_total_cnt = len(volumes)
        volume_up_count = 0
        for volume in volumes:
            if volume.get('status') == 'Started':
                volume_up_count = volume_up_count + 1
        return (
            volume_total_cnt,
            volume_total_cnt - volume_up_count,
            volume_up_count
        )

    def _get_volume_brick_statuses(self, volume):
        ret_val = {}
        for sub_volume_index, sub_volume_bricks in volume.get(
            'bricks',
            []
        ).iteritems():
            for brick in sub_volume_bricks:
                brick_hostname = brick.get('hostname')
                if (
                    brick_hostname == socket.gethostbyname(
                        self.CONFIG['peer_name']
                    ) or
                    brick_hostname == self.CONFIG['peer_name']
                ):
                    if 'status' in brick:
                        brick_statuses = ret_val.get(brick['hostname'], [])
                        status = \
                            gluster_utils.get_brick_state_mapping(
                                brick['status']
                            )
                        brick_statuses.append(
                            {
                                'status': status,
                                'path': brick['path']
                            }
                        )
                        ret_val[brick['hostname']] = brick_statuses
        return ret_val

    def _get_node_brick_status_wise_counts(self, volumes):
        ret_val = {}
        total = 0
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
                        if 'status' in brick:
                            status = \
                                gluster_utils.get_tendrl_volume_status(
                                    brick['status']
                                )
                            ret_val[status] = ret_val.get(status, 0) + 1
                            total = total + 1
        return ret_val

    def get_metrics(self):
        try:
            ret_val = {}
            # Push Peer status wise and total counts
            ret_val[
                'clusters.%s.nodes_count.total' % (
                    self.CONFIG['integration_id']
                )
            ], ret_val[
                'clusters.%s.nodes_count.down' % (
                    self.CONFIG['integration_id']
                )
            ], ret_val[
                'clusters.%s.nodes_count.up' % (
                    self.CONFIG['integration_id']
                )
            ] = self._get_peer_count()
            volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
            for volume in volumes:
                brick_statuses = self._get_volume_brick_statuses(volume)
                for host_name, bricks in brick_statuses.iteritems():
                    for brick in bricks:
                        # Push brick statuses
                        ret_val[
                            'clusters.%s.volumes.%s.nodes.%s.bricks.%s.'
                            'status' % (
                                self.CONFIG['integration_id'],
                                volume.get('name', ''),
                                self.CONFIG['peer_name'].replace('.', '_'),
                                brick['path'].replace('/', '|')
                            )
                        ] = brick['status']
                        ret_val[
                            'clusters.%s.nodes.%s.bricks.%s.status' % (
                                self.CONFIG['integration_id'],
                                self.CONFIG['peer_name'].replace('.', '_'),
                                brick['path'].replace('/', '|')
                            )
                        ] = brick['status']
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
            # Push volume statuses
            volume_statuses = self._get_volume_statuses()
            for vol_name, status_val in volume_statuses.iteritems():
                ret_val[
                    'clusters.%s.volumes.%s.status' % (
                        self.CONFIG['integration_id'],
                        vol_name
                    )
                ] = status_val
            # Push volume status wise counts
            ret_val[
                'clusters.%s.volume_count.total' % (
                    self.CONFIG['integration_id']
                )
            ], ret_val[
                'clusters.%s.volume_count.down' % (
                    self.CONFIG['integration_id']
                )
            ], ret_val[
                'clusters.%s.volume_count.up' % (
                    self.CONFIG['integration_id']
                )
            ] = self._get_volume_status_wise_counts()
            # Push Volume wise brick total count
            for volume in volumes:
                ret_val[
                    'clusters.%s.volumes.%s.brick_count.total' % (
                        self.CONFIG['integration_id'],
                        vol_name
                    )
                ] = int(volume.get('brick_count', 0))
            # Push node wise brick status wise counts
            brick_status_wise_counts = \
                self._get_node_brick_status_wise_counts(volumes)
            t_name = 'clusters.%s.nodes.%s.brick_count.%s'
            for status, val in brick_status_wise_counts.iteritems():
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        self.CONFIG['peer_name'].replace('.', '_'),
                        status
                    )
                ] = val
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
                    'clusters.%s.volumes.%s.rebalance_bytes' % (
                        self.CONFIG['integration_id'],
                        vol_name
                    )
                ] = int(filter(str.isdigit, rebalance_bytes))
            # Push rebalance files progress
            for vol_name, rebalance_files in self._get_vol_rebalance_files(
            ).iteritems():
                ret_val[
                    'clusters.%s.volumes.%s.rebalance_files' % (
                        self.CONFIG['integration_id'],
                        vol_name
                    )
                ] = rebalance_files
            # Push rebalance failures
            for vol_name, r_failures in self._get_volume_rebalance_failures(
            ).iteritems():
                ret_val[
                    'clusters.%s.volumes.%s.rebalance_failures' % (
                        self.CONFIG['integration_id'],
                        vol_name
                    )
                ] = r_failures
            # Push rebalance skipped
            for vol_name, r_skipped in self._get_volume_rebalance_skipped(
            ).iteritems():
                ret_val[
                    'clusters.%s.volumes.%s.rebalance_skipped' % (
                        self.CONFIG['integration_id'],
                        vol_name
                    )
                ] = r_skipped
            # Push cluster wise brick total count
            cluster_brick_count = 0
            for volume in volumes:
                cluster_brick_count = cluster_brick_count + int(
                    volume.get(
                        'brick_count',
                        0
                    )
                )
            ret_val[
                'clusters.%s.brick_count.total' % (
                    self.CONFIG['integration_id']
                )
            ] = cluster_brick_count
            return ret_val
        except (AttributeError, KeyError, ValueError):
            collectd.error(
                'Failed to fetch counters. Error %s\n\n' % (
                    traceback.format_exc()
                )
            )
            return {}
