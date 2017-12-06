import collectd
import time
import traceback
# import threading

import utils as tendrl_glusterfs_utils


ret_val = {}


def _parse_self_heal_info_stats(op):
    volume_heal_info = {}
    info = op.split("\n\n")
    for entry in info[:len(info) - 1]:
        brick_heal_info = {}
        brick_name = ""
        heal_pending_cnt = 0
        for line in entry.split("\n"):
            if "Brick " in line:
                brick_name = line.split(" ")[1]
            if "Number of entries:" in line:
                try:
                    heal_pending_cnt = int(line.split(": ")[1])
                except ValueError:
                    # Sometimes the values are returned as `-`
                    # if brick disconnected. Default to 0 in
                    # that case
                    heal_pending_cnt = 0
        brick_heal_info['heal_pending_cnt'] = heal_pending_cnt
        volume_heal_info[brick_name] = brick_heal_info

    return volume_heal_info


def _parse_self_heal_info_split_brain_stats(op):
    volume_heal_info = {}
    info = op.split("\n\n")
    for entry in info[:len(info) - 1]:
        brick_heal_info = {}
        brick_name = ""
        split_brain_cnt = 0
        for line in entry.split("\n"):
            if "Brick " in line:
                brick_name = line.split(" ")[1]
            if "Number of entries in split-brain:" in line:
                try:
                    split_brain_cnt = int(line.split(": ")[1])
                except ValueError:
                    # Sometimes the values are returned as `-`
                    # if brick disconnected. Default to 0 in
                    # that case
                    split_brain_cnt = 0
        brick_heal_info['split_brain_cnt'] = split_brain_cnt
        volume_heal_info[brick_name] = brick_heal_info

    return volume_heal_info


def get_volume_heal_info_split_brain_stats(vol):
    for trial_cnt in xrange(0, 3):
        vol_heal_op, vol_heal_err = \
            tendrl_glusterfs_utils.exec_command(
                "gluster volume heal %s info split-brain" % vol['name']
            )
        if vol_heal_err:
            time.sleep(5)
            if trial_cnt == 2:
                collectd.error(
                    'Failed to fetch volume heal info split-brain.'
                    'The error is: %s' % (
                        vol_heal_err
                    )
                )
                return {}
            continue
        else:
            break
    try:
        vol_heal_info = _parse_self_heal_info_split_brain_stats(
            vol_heal_op
        )
        return vol_heal_info
    except (
        AttributeError,
        KeyError,
        ValueError
    ):
        collectd.error(
            'Failed to collect volume heal info split-brain. Error %s' % (
                traceback.format_exc()
            )
        )
        return {}


def get_volume_heal_info_stats(vol):
    for trial_cnt in xrange(0, 3):
        vol_heal_op, vol_heal_err = \
            tendrl_glusterfs_utils.exec_command(
                "gluster volume heal %s info" % vol['name']
            )
        if vol_heal_err:
            time.sleep(5)
            if trial_cnt == 2:
                collectd.error(
                    'Failed to fetch volume heal info.'
                    'The error is: %s' % (
                        vol_heal_err
                    )
                )
                return {}
            continue
        else:
            break
    try:
        vol_heal_info = _parse_self_heal_info_stats(
            vol_heal_op
        )
        return vol_heal_info
    except (
        AttributeError,
        KeyError,
        ValueError
    ):
        collectd.error(
            'Failed to collect volume heal info. Error %s' % (
                traceback.format_exc()
            )
        )
        return {}


def get_heal_info(volume, integration_id):
    vol_heal_info_stats = get_volume_heal_info_stats(volume)
    vol_heal_info_split_brain_stats = get_volume_heal_info_split_brain_stats(volume)
    for key, value in vol_heal_info_stats.iteritems():
        if key == "" or value is None:
            continue
        t_name = \
            "clusters.%s.volumes.%s.nodes.%s.bricks.%s.heal_pending_cnt"
        ret_val[
            t_name % (
                integration_id,
                volume['name'],
                key.split(":")[0].replace('.', '_'),
                key.split(":")[1].replace('/', '|')
            )
        ] = value['heal_pending_cnt']
    for key, value in vol_heal_info_split_brain_stats.iteritems():
        if key == "" or value is None:
            continue
        t_name = \
            "clusters.%s.volumes.%s.nodes.%s.bricks.%s.split_brain_cnt"
        ret_val[
            t_name % (
                integration_id,
                volume['name'],
                key.split(":")[0].replace('.', '_'),
                key.split(":")[1].replace('/', '|')
            )
        ] = value['split_brain_cnt']


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
