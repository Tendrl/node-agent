import collectd
import time
import traceback
# import threading

import utils as tendrl_glusterfs_utils

try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree


ret_val = {}


def _parse_heal_info_stats(tree, integration_id, etcd_client):
    bricks_dict = {}
    for brick in tree.findall("healInfo/bricks/brick"):
        brick_name = brick.find("name").text
        brick_host = brick_name.split(":")[0]
        brick_path = brick_name.split(":")[1]
        brick_host = tendrl_glusterfs_utils.find_brick_host(
            etcd_client, integration_id, brick_host
        )
        if not brick_host:
            continue
        try:
            no_of_entries = int(brick.find("numberOfEntries").text)
        except ValueError:
            no_of_entries = 0
        bricks_dict["%s:%s" % (brick_host, brick_path)] = no_of_entries
    return bricks_dict


def get_volume_heal_info_split_brain_stats(vol, integration_id, etcd_client):
    for trial_cnt in xrange(0, 3):
        vol_heal_op, vol_heal_err = \
            tendrl_glusterfs_utils.exec_command(
                "gluster volume heal %s info split-brain --nolog --xml" % vol['name']
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
        vol_heal_info = _parse_heal_info_stats(
            ElementTree.fromstring(vol_heal_op),
            integration_id, etcd_client
        )
        return vol_heal_info
    except (
        AttributeError,
        KeyError,
        ValueError,
        ElementTree.ParseError
    ):
        # For heal info command timeout and older version of glusterd
        # ElementTree will raise parser error
        collectd.error(
            'Failed to collect volume heal info split-brain. Error %s' % (
                traceback.format_exc()
            )
        )
        return {}


def get_volume_heal_info_stats(vol, integration_id, etcd_client):
    for trial_cnt in xrange(0, 3):
        vol_heal_op, vol_heal_err = \
            tendrl_glusterfs_utils.exec_command(
                "gluster volume heal %s info --nolog --xml" % vol['name']
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
        vol_heal_info = _parse_heal_info_stats(
            ElementTree.fromstring(vol_heal_op),
            integration_id, etcd_client
        )
        return vol_heal_info
    except (
        AttributeError,
        KeyError,
        ValueError,
        ElementTree.ParseError
    ):
        collectd.error(
            'Failed to collect volume heal info. Error %s' % (
                traceback.format_exc()
            )
        )
        return {}


def get_heal_info(volume, integration_id, etcd_client, brick_path_separator):
    vol_heal_info_stats = get_volume_heal_info_stats(volume, integration_id,
                                                     etcd_client)
    vol_heal_info_split_brain_stats = get_volume_heal_info_split_brain_stats(
        volume, integration_id, etcd_client
    )
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
                key.split(":")[1].replace('/', brick_path_separator)
            )
        ] = value
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
                key.split(":")[1].replace('/', brick_path_separator)
            )
        ] = value


def get_heal_info_disperse(
    volume, integration_id, etcd_client, brick_path_separator
):
    vol_heal_info_stats = get_volume_heal_info_stats(
        volume, integration_id, etcd_client
    )
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
                key.split(":")[1].replace('/', brick_path_separator)
            )
        ] = value


def get_metrics(CLUSTER_TOPOLOGY, CONFIG, etcd_client, brick_path_separator):
    global ret_val
    # threads = []
    for volume in CLUSTER_TOPOLOGY.get('volumes', []):
        if 'Replicate' in volume.get('type', ''):
            get_heal_info(
                volume,
                CONFIG['integration_id'],
                etcd_client,
                brick_path_separator
            )
            # thread = threading.Thread(
            #    target=get_heal_info,
            #    args=(volume, CONFIG['integration_id'],)
            # )
            # thread.start()
            # threads.append(
            #    thread
            # )
        if 'Disperse' in volume.get('type', ''):
            get_heal_info_disperse(volume, CONFIG['integration_id'],
                                   etcd_client, brick_path_separator)
    # for thread in threads:
    #    thread.join(1)
    # for thread in threads:
    #    del thread
    return ret_val
