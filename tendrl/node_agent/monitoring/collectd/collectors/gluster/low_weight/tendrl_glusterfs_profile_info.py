import collectd
import gevent
import traceback
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree

import utils as tendrl_glusterfs_utils


PLUGIN_NAME = 'network_throughput'
CONFIG = {}
CLUSTER_TOPOLOGY = {}


def _parseVolumeProfileInfo(tree, nfs=False):
    bricks = []
    if nfs:
        brickKey = 'nfs'
        bricksKey = 'nfsServers'
    else:
        brickKey = 'brick'
        bricksKey = 'bricks'
    for brick in tree.findall('volProfile/brick'):
        fopCumulative = []
        blkCumulative = []
        fopInterval = []
        blkInterval = []
        brickName = brick.find('brickName').text
        for block in brick.findall('cumulativeStats/blockStats/block'):
            blkCumulative.append(
                {
                    'size': block.find('size').text,
                    'read': block.find('reads').text,
                    'write': block.find('writes').text
                }
            )
        for fop in brick.findall('cumulativeStats/fopStats/fop'):
            gevent.sleep(0.1)
            fopCumulative.append(
                {
                    'name': fop.find('name').text,
                    'hits': fop.find('hits').text,
                    'latencyAvg': fop.find('avgLatency').text,
                    'latencyMin': fop.find('minLatency').text,
                    'latencyMax': fop.find('maxLatency').text
                }
            )
        for block in brick.findall('intervalStats/blockStats/block'):
            gevent.sleep(0.1)
            blkInterval.append(
                {
                    'size': block.find('size').text,
                    'read': block.find('reads').text,
                    'write': block.find('writes').text
                }
            )
        for fop in brick.findall('intervalStats/fopStats/fop'):
            gevent.sleep(0.1)
            fopInterval.append(
                {
                    'name': fop.find('name').text,
                    'hits': fop.find('hits').text,
                    'latencyAvg': fop.find('avgLatency').text,
                    'latencyMin': fop.find('minLatency').text,
                    'latencyMax': fop.find('maxLatency').text
                }
            )
        bricks.append(
            {
                brickKey: brickName,
                'cumulativeStats': {
                    'blockStats': blkCumulative,
                    'fopStats': fopCumulative,
                    'duration': brick.find(
                        'cumulativeStats/duration'
                    ).text,
                    'totalRead': brick.find(
                        'cumulativeStats/totalRead'
                    ).text,
                    'totalWrite': brick.find(
                        'cumulativeStats/totalWrite'
                    ).text
                },
                'intervalStats': {
                    'blockStats': blkInterval,
                    'fopStats': fopInterval,
                    'duration': brick.find('intervalStats/duration').text,
                    'totalRead': brick.find(
                        'intervalStats/totalRead'
                    ).text,
                    'totalWrite': brick.find(
                        'intervalStats/totalWrite'
                    ).text
                }
            }
        )
    status = {
        'volumeName': tree.find("volProfile/volname").text,
        bricksKey: bricks
    }
    return status


def get_volume_profile_info(volName):
    global CONFIG
    ret_val = {}
    brickName = ''
    profile_info = {}
    profile_cmd_op, profile_err = tendrl_glusterfs_utils.exec_command(
        "gluster volume profile %s info --xml" % volName
    )
    if profile_err:
        collectd.error(
            'Failed to fetch brick utilizations. The error is: %s' % (
                profile_err
            )
        )
        return ret_val
    try:
        profile_info = _parseVolumeProfileInfo(
            ElementTree.fromstring(profile_cmd_op)
        )
        return profile_info
    except (
        AttributeError,
        KeyError,
        ValueError
    ):
        collectd.error(
            'Failed to collect iops details of brick %s in volume %s of '
            'cluster %s. The profile info is %s. Error %s' % (
                brickName,
                volName,
                CONFIG['integration_id'],
                str(profile_info),
                traceback.format_exc()
            )
        )
        return ret_val


def get_metrics():
    global CONFIG
    global CLUSTER_TOPOLOGY
    ret_val = {}
    volumes = CLUSTER_TOPOLOGY.get('volumes', [])
    for volume in volumes:
        volName = volume['name']
        vol_iops = get_volume_profile_info(volName)
        if not vol_iops:
            return ret_val
        for brick_det in vol_iops.get('bricks', {}):
            brickName = brick_det.get('brick', '')
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s.iops." \
                "gauge-read"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    volName,
                    CONFIG['peer_name'].replace('.', '_'),
                    brickName.split(':')[1].replace('/', '|')
                )
            ] = brick_det.get('cumulativeStats').get('totalRead')
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s.iops." \
                "gauge-write"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    volName,
                    CONFIG['peer_name'].replace('.', '_'),
                    brickName.split(':')[1].replace('/', '|')
                )
            ] = brick_det.get('cumulativeStats').get('totalWrite')
            gevent.sleep(0.1)
    return ret_val


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
