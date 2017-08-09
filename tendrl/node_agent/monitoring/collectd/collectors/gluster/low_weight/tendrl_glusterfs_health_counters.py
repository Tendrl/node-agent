import collectd
import socket
import sys
import traceback

sys.path.append('/usr/lib64/collectd/gluster')
import utils as tendrl_glusterfs_utils
sys.path.remove('/usr/lib64/collectd/gluster')


CLUSTER_TOPOLOGY = {}
CONFIG = {}
PEER_IN_CLUSTER = ['Peer', 'in', 'Cluster']


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


def get_volume_statuses():
    global CLUSTER_TOPOLOGY
    ret_val = {}
    volumes = CLUSTER_TOPOLOGY.get('volumes', [])
    for volume in volumes:
        status = volume.get('status', '')
        ret_val[volume['name']] = \
            tendrl_glusterfs_utils.get_volume_state_mapping(status)
    return ret_val


def get_volume_snap_counts():
    global CLUSTER_TOPOLOGY
    ret_val = {}
    volumes = CLUSTER_TOPOLOGY.get('volumes', [])
    for volume in volumes:
        snap_cnt = volume.get('snap_count', 0)
        ret_val[volume['name']] = snap_cnt
    return ret_val


def get_vol_rebalance_in_progress_bytes():
    global CLUSTER_TOPOLOGY
    ret_val = {}
    volumes = CLUSTER_TOPOLOGY.get('volumes', [])
    for volume in volumes:
        rebalance_data = volume.get('rebalance_data', 0)
        ret_val[volume['name']] = rebalance_data
    return ret_val


def get_vol_rebalance_in_progress_files():
    global CLUSTER_TOPOLOGY
    ret_val = {}
    volumes = CLUSTER_TOPOLOGY.get('volumes', [])
    for volume in volumes:
        rebalance_files = volume.get('rebalance_files', 0)
        ret_val[volume['name']] = rebalance_files
    return ret_val


def get_volume_rebalance_failures():
    global CLUSTER_TOPOLOGY
    ret_val = {}
    volumes = CLUSTER_TOPOLOGY.get('volumes', [])
    for volume in volumes:
        rebalance_failures = volume.get('rebalance_failures', 0)
        ret_val[volume['name']] = rebalance_failures
    return ret_val


def get_volume_rebalance_skipped():
    global CLUSTER_TOPOLOGY
    ret_val = {}
    volumes = CLUSTER_TOPOLOGY.get('volumes', [])
    for volume in volumes:
        rebalance_skipped = volume.get('rebalance_skipped', 0)
        ret_val[volume['name']] = rebalance_skipped
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
        []
    ).iteritems():
        for brick in sub_volume_bricks:
            brick_hostname = brick.get('hostname')
            if (
                brick_hostname == socket.gethostbyname(
                    CONFIG['peer_name']
                ) or
                brick_hostname == CONFIG['peer_name']
            ):
                if 'status' in brick:
                    brick_statuses = ret_val.get(brick['hostname'], [])
                    status = tendrl_glusterfs_utils.get_brick_state_mapping(
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


def get_node_brick_status_wise_counts(volumes):
    global CONFIG
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
                        CONFIG['peer_name']
                    ) or
                    brick_hostname == CONFIG['peer_name']
                ):
                    if 'status' in brick:
                        status = \
                            tendrl_glusterfs_utils.get_tendrl_volume_status(
                                brick['status']
                            )
                        ret_val[status] = ret_val.get(status, 0) + 1
                        total = total + 1
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
        volumes = CLUSTER_TOPOLOGY.get('volumes', [])
        for volume in volumes:
            brick_statuses = get_volume_brick_statuses(volume)
            for host_name, bricks in brick_statuses.iteritems():
                for brick in bricks:
                    # Push brick statuses
                    ret_val[
                        'clusters.%s.volumes.%s.nodes.%s.bricks.%s.status' % (
                            CONFIG['integration_id'],
                            volume.get('name', ''),
                            CONFIG['peer_name'].replace('.', '_'),
                            brick['path'].replace('/', '|')
                        )
                    ] = brick['status']
                    ret_val[
                        'clusters.%s.nodes.%s.bricks.%s.status' % (
                            CONFIG['integration_id'],
                            CONFIG['peer_name'].replace('.', '_'),
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
                            CONFIG['peer_name']
                        ) or
                        brick_hostname == CONFIG['peer_name']
                    ):
                        # Push brick client connections
                        ret_val[
                            'clusters.%s.volumes.%s.nodes.%s.bricks.%s.'
                            'connections_count' % (
                                CONFIG['integration_id'],
                                volume.get('name', ''),
                                CONFIG['peer_name'].replace('.', '_'),
                                brick['path'].replace('/', '|')
                            )
                        ] = brick['connections_count']
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
        # Push node wise brick status wise counts
        brick_status_wise_counts = \
            get_node_brick_status_wise_counts(volumes)
        t_name = 'clusters.%s.nodes.%s.brick_count.%s'
        for status, val in brick_status_wise_counts.iteritems():
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    CONFIG['peer_name'].replace('.', '_'),
                    status
                )
            ] = val
        # Push volume wise snap counts
        for vol_name, snap_cnt in get_volume_snap_counts().iteritems():
            ret_val[
                'clusters.%s.volumes.%s.snap_count' % (
                    CONFIG['integration_id'],
                    vol_name
                )
            ] = snap_cnt
        # Push rebalance bytes progress
        for vol_name, rebalance_bytes in get_vol_rebalance_in_progress_bytes(
        ).iteritems():
            ret_val[
                'clusters.%s.volumes.%s.rebalance_bytes' % (
                    CONFIG['integration_id'],
                    vol_name
                )
            ] = int(filter(str.isdigit, rebalance_bytes))
        # Push rebalance files progress
        for vol_name, rebalance_files in get_vol_rebalance_in_progress_files(
        ).iteritems():
            ret_val[
                'clusters.%s.volumes.%s.rebalance_files' % (
                    CONFIG['integration_id'],
                    vol_name
                )
            ] = rebalance_files
        # Push rebalance failures
        for vol_name, rebalance_failures in get_volume_rebalance_failures(
        ).iteritems():
            ret_val[
                'clusters.%s.volumes.%s.rebalance_failures' % (
                    CONFIG['integration_id'],
                    vol_name
                )
            ] = rebalance_failures
        # Push rebalance skipped
        for vol_name, rebalance_skipped in get_volume_rebalance_skipped(
        ).iteritems():
            ret_val[
                'clusters.%s.volumes.%s.rebalance_skipped' % (
                    CONFIG['integration_id'],
                    vol_name
                )
            ] = rebalance_skipped
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
