import collectd
import traceback

import tendrl_glusterfs_base
import glusterfs.utils as tendrl_glusterfs_utils


PEER_IN_CLUSTER = ['Peer', 'in', 'Cluster']


class TendrlGlusterfsHealthCounters(
    tendrl_glusterfs_base.TendrlGlusterfsMonitoringBase
):
    def __init__(self):
        tendrl_glusterfs_base.TendrlGlusterfsMonitoringBase.__init__(self)

    def get_peer_count(self):
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
                        set(peer['state']) & set(PEER_IN_CLUSTER)
                    ) == len(PEER_IN_CLUSTER)
                )
            ):
                peer_down_cnt = peer_down_cnt + 1
        return peer_total_cnt, peer_down_cnt

    def get_volume_statuses(self):
        ret_val = {}
        volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
        for volume in volumes:
            status = volume.get('status', '')
            ret_val[volume['name']] = \
                tendrl_glusterfs_utils.get_volume_state_mapping(status)
        return ret_val

    def get_volume_status_wise_counts(self):
        volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
        volume_total_cnt = len(volumes)
        volume_down_count = 0
        for volume in volumes:
            if volume.get('status') is not 'Started':
                volume_down_count = volume_down_count + 1
        return volume_total_cnt, volume_down_count

    def get_volume_brick_statuses(self, volume):
        ret_val = {}
        for sub_volume_index, sub_volume_bricks in volume.get(
            'bricks',
            {}
        ).iteritems():
            for brick in sub_volume_bricks:
                if 'status' in brick:
                    brick_statuses = ret_val.get(brick['hostname'], [])
                    brick_statuses.append(
                        {
                            brick['path']: tendrl_glusterfs_utils.get_brick_state_mapping(
                                brick['status']
                            )
                        }
                    )
                    ret_val['hostname'] = brick_statuses
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
            ] = self.get_peer_count()
            # Push brick statuses
            volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
            for volume in volumes:
                brick_statuses = self.get_volume_brick_statuses(volume)
                for host_name, brick in brick_statuses.iteritems():
                    for path, status_val in brick.iteritems():
                        ret_val[
                            'clusters.%s.volumes.%s.bricks_count' % (
                                self.CONFIG['integration_id'],
                                volume.get('name', ''),
                            )
                        ] = status_val
            # Push volume statuses
            volume_statuses = self.get_volume_statuses()
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
            ] = self.get_volume_status_wise_counts()
            # Push Volume wise brick total count
            for volume in volumes:
                ret_val[
                    'clusters.%s.volumes.%s.brick_count.total' % (
                        self.CONFIG['integration_id'],
                        vol_name
                    )
                ] = int(volume.get('brick_count', 0))
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
