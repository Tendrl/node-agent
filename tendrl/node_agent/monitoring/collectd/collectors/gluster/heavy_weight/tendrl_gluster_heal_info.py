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


def _parse_heal_info_stats(tree):
    bricks_dict = {}
    for brick in tree.findall("healInfo/bricks/brick"):
        brick_name = brick.find("name").text
        brick_host = brick_name.split(":")[0]
        brick_path = brick_name.split(":")[1]

        # If brick host is returned as an IP conver to FQDN
        try:
            from IPy import IP
            from dns import resolver, reversename
            IP(brick_host)
            addr = reversename.from_address(brick_host)
            brick_host = str(resolver.query(addr, "PTR")[0])[:-1]
        except ValueError:
            pass

        no_of_entries = 0
        try:
            no_of_entries = int(brick.find("numberOfEntries").text)
        except ValueError:
            no_of_entries = 0
        bricks_dict["%s:%s" % (brick_host, brick_path)] = no_of_entries
    return bricks_dict


def get_volume_heal_info_split_brain_stats(vol):
    for trial_cnt in xrange(0, 3):
        vol_heal_op, vol_heal_err = \
            tendrl_glusterfs_utils.exec_command(
                "gluster volume heal %s info split-brain --xml" % vol['name']
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
            ElementTree.fromstring(vol_heal_op)
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
                "gluster volume heal %s info --xml" % vol['name']
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
            ElementTree.fromstring(vol_heal_op)
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
                key.split(":")[1].replace('/', '|')
            )
        ] = value


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
