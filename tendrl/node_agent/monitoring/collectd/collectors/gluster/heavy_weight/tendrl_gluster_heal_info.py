import collectd
import sys
import traceback

sys.path.append('/usr/lib64/collectd/gluster')
import utils as tendrl_glusterfs_utils
sys.path.remove('/usr/lib64/collectd/gluster')


CLUSTER_TOPOLOGY = {}
CONFIG = {}


def _parse_self_heal_stats(op):
    info = op.split('Crawl statistics for brick no ')
    bricks_heal_info = []
    for i in range(1, len(info)):
        brick_i_info = info[i].split('\n')
        brick_heal_info = {}
        for idx, line in enumerate(brick_i_info):
            line = line.strip()
            if idx == 0:
                brick_heal_info['brick_index'] = int(line) + 1
            if 'No. of entries healed' in line:
                brick_heal_info['healed_cnt'] = int(
                    line.replace('No. of entries healed: ', '')
                )
            if 'No. of entries in split-brain' in line:
                brick_heal_info['split_brain_cnt'] = int(
                    line.replace('No. of entries in split-brain: ', '')
                )
            if 'No. of heal failed entries' in line:
                brick_heal_info['heal_failed_cnt'] = int(
                    line.replace('No. of heal failed entries: ', '')
                )
            if 'Hostname of brick ' in line:
                brick_heal_info['host_name'] = line.replace(
                    'Hostname of brick ', ''
                )
        bricks_heal_info.append(brick_heal_info)
    return bricks_heal_info


def get_volume_heal_info(vol):
    ret_val = {}
    vol_heal_op, vol_heal_err = \
        tendrl_glusterfs_utils.exec_command(
            "gluster volume heal %s statistics" % vol['name']
        )
    if vol_heal_err:
        collectd.error(
            'Failed to fetch volume heal statistics. The error is: %s' % (
                vol_heal_err
            )
        )
        return ret_val
    try:
        vol_heal_info = _parse_self_heal_stats(
            vol_heal_op
        )
        for idx, brick_heal_info in enumerate(vol_heal_info):
            for sub_vol_id, sub_vol in vol['bricks'].iteritems():
                for sub_vol_brick in sub_vol:
                    if (
                        sub_vol_brick[
                            'index'
                        ] == brick_heal_info['brick_index']
                    ):
                        vol_heal_info[idx][
                            'brick_path'
                        ] = sub_vol_brick['path']
        return vol_heal_info
    except (
        AttributeError,
        KeyError,
        ValueError
    ):
        collectd.error(
            'Failed to collect volume heal statistics. Error %s' % (
                traceback.format_exc()
            )
        )
        return ret_val


def get_metrics():
    global CLUSTER_TOPOLOGY
    global CONFIG
    ret_val = {}
    for volume in CLUSTER_TOPOLOGY.get('volumes', []):
        if 'Replicate' in volume.get('type', ''):
            vol_heal_info = get_volume_heal_info(volume)
            for brick_heal_info in vol_heal_info:
                t_name = \
                    'clusters.%s.volumes.%s.nodes.%s.bricks.%s.split_brain_cnt'
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        volume['name'],
                        brick_heal_info['host_name'].replace('.', '_'),
                        brick_heal_info['brick_path'].replace('/', '|')
                    )
                ] = brick_heal_info['split_brain_cnt']
                t_name = \
                    'clusters.%s.volumes.%s.nodes.%s.bricks.%s.healed_cnt'
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        volume['name'],
                        brick_heal_info['host_name'].replace('.', '_'),
                        brick_heal_info['brick_path'].replace('/', '|')
                    )
                ] = brick_heal_info['healed_cnt']
                t_name = \
                    'clusters.%s.volumes.%s.nodes.%s.bricks.%s.heal_failed_cnt'
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        volume['name'],
                        brick_heal_info['host_name'].replace('.', '_'),
                        brick_heal_info['brick_path'].replace('/', '|')
                    )
                ] = brick_heal_info['heal_failed_cnt']
    return ret_val


def read_callback():
    global CLUSTER_TOPOLOGY
    global CONFIG
    CLUSTER_TOPOLOGY = \
        tendrl_glusterfs_utils.get_gluster_cluster_topology()
    try:
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
    except (
        AttributeError,
        KeyError,
        ValueError
    ):
        collectd.error(
            'Error in heal info: %s\n\n' % (
                str(traceback.format_exc())
            )
        )


def configure_callback(configobj):
    global CONFIG
    CONFIG = {
        c.key: c.values[0] for c in configobj.children
    }


collectd.register_config(configure_callback)
collectd.register_read(read_callback, 600)

