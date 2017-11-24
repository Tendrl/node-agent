import collectd
import time
import traceback
# import threading

import utils as tendrl_glusterfs_utils


ret_val = {}


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
    ret_val = []
    for trial_cnt in xrange(0, 3):
        vol_heal_op, vol_heal_err = \
            tendrl_glusterfs_utils.exec_command(
                "gluster volume heal %s statistics" % vol['name']
            )
        if vol_heal_err:
            time.sleep(5)
            if trial_cnt == 2:
                collectd.error(
                    'Failed to fetch volume heal statistics.'
                    'The error is: %s' % (
                        vol_heal_err
                    )
                )
                return ret_val
            continue
        else:
            break
    try:
        vol_heal_info = _parse_self_heal_stats(
            vol_heal_op
        )
        for idx, brick_heal_info in enumerate(vol_heal_info):
            for sub_vol_id, sub_vol in vol['bricks'].iteritems():
                for brick_idx, sub_vol_brick in enumerate(sub_vol):
                    if (
                        sub_vol_brick[
                            'brick_index'
                        ] == brick_heal_info[
                            'brick_index'
                        ]
                    ) and sub_vol_brick['hostname'] == brick_heal_info["host_name"]:
                        vol_heal_info[idx][
                            'brick_path'
                        ] = sub_vol_brick['path']
                        ret_val.append(vol_heal_info[idx])
        return ret_val
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


def get_heal_info(volume, integration_id):
    vol_heal_info = get_volume_heal_info(volume)
    for brick_heal_info in vol_heal_info:
        t_name = \
            'clusters.%s.volumes.%s.nodes.%s.bricks.%s.split_brain_cnt'
        ret_val[
            t_name % (
                integration_id,
                volume['name'],
                brick_heal_info['host_name'].replace('.', '_'),
                brick_heal_info['brick_path'].replace('/', '|')
            )
        ] = brick_heal_info['split_brain_cnt']
        t_name = \
            'clusters.%s.volumes.%s.nodes.%s.bricks.%s.healed_cnt'
        ret_val[
            t_name % (
                integration_id,
                volume['name'],
                brick_heal_info['host_name'].replace('.', '_'),
                brick_heal_info['brick_path'].replace('/', '|')
            )
        ] = brick_heal_info['healed_cnt']
        t_name = \
            'clusters.%s.volumes.%s.nodes.%s.bricks.%s.heal_failed_cnt'
        ret_val[
            t_name % (
                integration_id,
                volume['name'],
                brick_heal_info['host_name'].replace('.', '_'),
                brick_heal_info['brick_path'].replace('/', '|')
            )
        ] = brick_heal_info['heal_failed_cnt']


def get_metrics(CLUSTER_TOPOLOGY, CONFIG):
    global ret_val
    # threads = []
    for volume in CLUSTER_TOPOLOGY.get('volumes', []):
        if 'Replicate' in volume.get('type', ''):
            get_heal_info(volume, CONFIG['integration_id'])
            # thread = threading.Thread(
            #    target=get_heal_info,
            #    args=(volume, CONFIG['integration_id'],)
            # )
            # thread.start()
            # threads.append(
            #    thread
            # )
    # for thread in threads:
    #    thread.join(1)
    # for thread in threads:
    #    del thread
    return ret_val
