import collectd
import traceback

import utils as tendrl_glusterfs_utils


PEER_IN_CLUSTER = ['Peer', 'in', 'Cluster']
CLUSTER_TOPOLOGY = {}
CONFIG = {}


def get_peer_count():
    global CLUSTER_TOPOLOGY
    global PEER_IN_CLUSTER
    peer_down_cnt = 0
    peers = CLUSTER_TOPOLOGY.get('peers', [])
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
    return (
        peer_total_cnt,
        peer_down_cnt,
        peer_total_cnt - peer_down_cnt
    )


def get_volume_statuses():
    global CLUSTER_TOPOLOGY
    ret_val = {}
    volumes = CLUSTER_TOPOLOGY.get('volumes', [])
    for volume in volumes:
        status = volume.get('status', '')
        ret_val[volume['name']] = \
            tendrl_glusterfs_utils.get_volume_state_mapping(status)
    return ret_val


def get_volume_status_wise_counts():
    global CLUSTER_TOPOLOGY
    volumes = CLUSTER_TOPOLOGY.get('volumes', [])
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


def get_volume_brick_statuses(volume):
    ret_val = {}
    for sub_volume_index, sub_volume_bricks in volume.get(
        'bricks',
        {}
    ).iteritems():
        for brick in sub_volume_bricks:
            if 'status' in brick:
                brick_statuses = ret_val.get(brick['hostname'], [])
                b_path = tendrl_glusterfs_utils.get_brick_state_mapping(
                    brick['status']
                )
                brick_statuses.append(
                    {
                        brick['path']: b_path
                    }
                )
                ret_val['hostname'] = brick_statuses
    return ret_val


def get_metrics():
    global CLUSTER_TOPOLOGY
    global CONFIG
    try:
        ret_val = {}
        # Push Peer status wise and total counts
        ret_val[
            'clusters.%s.nodes_count.total' % (
                CONFIG['integration_id']
            )
        ], ret_val[
            'clusters.%s.nodes_count.down' % (
                CONFIG['integration_id']
            )
        ], ret_val[
            'clusters.%s.nodes_count.up' % (
                CONFIG['integration_id']
            )
        ] = get_peer_count()
        # Push brick statuses
        volumes = CLUSTER_TOPOLOGY.get('volumes', [])
        for volume in volumes:
            brick_statuses = get_volume_brick_statuses(volume)
            for host_name, brick in brick_statuses.iteritems():
                for path, status_val in brick.iteritems():
                    ret_val[
                        'clusters.%s.volumes.%s.bricks_count' % (
                            CONFIG['integration_id'],
                            volume.get('name', ''),
                        )
                    ] = status_val
        # Push volume statuses
        volume_statuses = get_volume_statuses()
        for vol_name, status_val in volume_statuses.iteritems():
            ret_val[
                'clusters.%s.volumes.%s.status' % (
                    CONFIG['integration_id'],
                    vol_name
                )
            ] = status_val
        # Push volume status wise counts
        ret_val[
            'clusters.%s.volume_count.total' % (
                CONFIG['integration_id']
            )
        ], ret_val[
            'clusters.%s.volume_count.down' % (
                CONFIG['integration_id']
            )
        ], ret_val[
            'clusters.%s.volume_count.up' % (
                CONFIG['integration_id']
            )
        ] = get_volume_status_wise_counts()
        # Push Volume wise brick total count
        for volume in volumes:
            ret_val[
                'clusters.%s.volumes.%s.brick_count.total' % (
                    CONFIG['integration_id'],
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
                CONFIG['integration_id']
            )
        ] = cluster_brick_count
        return ret_val
    except (AttributeError, KeyError, ValueError):
        collectd.error(
            'Failed to fetch counters. Error %s\n\n' % (
                traceback.format_exc()
            )
        )


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
