import collectd
import gevent
import socket
import sys
import traceback
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree


sys.path.append('/usr/lib64/collectd/gluster')
import utils as tendrl_glusterfs_utils
sys.path.remove('/usr/lib64/collectd/gluster')


PLUGIN_NAME = 'network_throughput'
CONFIG = {}
CLUSTER_TOPOLOGY = {}
READ_WRITE_OPS = [
    'CREATE',
    'DISCARD',
    'FALLOCATE',
    'FLUSH',
    'FSYNC',
    'FSYNCDIR',
    'RCHECKSUM',
    'READ',
    'READDIR',
    'READDIRP',
    'READY',
    'WRITE',
    'ZEROFILL'
]
LOCK_OPS = [
    'ENTRYLK',
    'FENTRYLK',
    'FINODELK',
    'INODELK',
    'LK'
]
INODE_OPS = [
    'ACCESS',
    'FGETXATTR',
    'FREMOVEXATTR',
    'FSETATTR',
    'FSETXATTR',
    'FSTAT',
    'FTRUNCATE',
    'FXATTROP',
    'GETXATTR',
    'LOOKUP',
    'OPEN',
    'OPENDIR',
    'READLINK',
    'REMOVEXATTR',
    'SEEK',
    'SETATTR',
    'SETXATTR',
    'STAT',
    'STATFS',
    'TRUNCATE',
    'XATTROP'
]
ENTRY_OPS = [
    'LINK',
    'MKDIR',
    'MKNOD',
    'RENAME',
    'RMDIR',
    'SYMLINK',
    'UNLINK'
]


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
        ValueError,
        ElementTree.ParseError
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
    global READ_WRITE_OPS
    global LOCK_OPS
    global INODE_OPS
    global ENTRY_OPS
    ret_val = {}
    volumes = CLUSTER_TOPOLOGY.get('volumes', [])
    for volume in volumes:
        volName = volume['name']
        vol_iops = get_volume_profile_info(volName)
        if not vol_iops:
            return ret_val
        read_write_hits = 0
        inode_hits = 0
        entry_hits = 0
        lock_hits = 0
        for brick_det in vol_iops.get('bricks', {}):
            brickName = brick_det.get('brick', '')
            brick_host = brick_det.get('hostname', '')
            if (
                brick_host == CONFIG['peer_name'] or
                brick_host == socket.gethostbyname(
                    CONFIG['peer_name']
                )
            ):
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s.iops." \
                    "gauge-read"
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        volName,
                        CONFIG['peer_name'].replace('.', '_'),
                        brickName.split(':')[1].replace('/', '|')
                    )
                ] = brick_det.get('intervalStats').get('totalRead')
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s.iops." \
                    "gauge-write"
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        volName,
                        CONFIG['peer_name'].replace('.', '_'),
                        brickName.split(':')[1].replace('/', '|')
                    )
                ] = brick_det.get('intervalStats').get('totalWrite')
                t_name = "clusters.%s.nodes.%s.bricks.%s.iops." \
                    "gauge-read"
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        CONFIG['peer_name'].replace('.', '_'),
                        brickName.split(':')[1].replace('/', '|')
                    )
                ] = brick_det.get('intervalStats').get('totalRead')
                t_name = "clusters.%s.nodes.%s.bricks.%s.iops." \
                    "gauge-write"
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        CONFIG['peer_name'].replace('.', '_'),
                        brickName.split(':')[1].replace('/', '|')
                    )
                ] = brick_det.get('intervalStats').get('totalWrite')
                fopIntervalStats = brick_det.get(
                    'intervalStats'
                ).get('fopStats')
                for fopStat in fopIntervalStats:
                    t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s.fop." \
                        "%s.hits"
                    ret_val[
                        t_name % (
                            CONFIG['integration_id'],
                            volName,
                            CONFIG['peer_name'].replace('.', '_'),
                            brickName.split(':')[1].replace('/', '|'),
                            fopStat.get('name')
                        )
                    ] = float(fopStat.get('hits'))
                    t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s.fop." \
                        "%s.latencyAvg"
                    ret_val[
                        t_name % (
                            CONFIG['integration_id'],
                            volName,
                            CONFIG['peer_name'].replace('.', '_'),
                            brickName.split(':')[1].replace('/', '|'),
                            fopStat.get('name')
                        )
                    ] = float(fopStat.get('latencyAvg'))
                    t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s.fop." \
                        "%s.latencyMin"
                    ret_val[
                        t_name % (
                            CONFIG['integration_id'],
                            volName,
                            CONFIG['peer_name'].replace('.', '_'),
                            brickName.split(':')[1].replace('/', '|'),
                            fopStat.get('name')
                        )
                    ] = float(fopStat.get('latencyMin'))
                    t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s.fop." \
                        "%s.latencyMax"
                    ret_val[
                        t_name % (
                            CONFIG['integration_id'],
                            volName,
                            CONFIG['peer_name'].replace('.', '_'),
                            brickName.split(':')[1].replace('/', '|'),
                            fopStat.get('name')
                        )
                    ] = float(fopStat.get('latencyMax'))
                    t_name = "clusters.%s.nodes.%s.bricks.%s.fop." \
                        "%s.hits"
                    ret_val[
                        t_name % (
                            CONFIG['integration_id'],
                            CONFIG['peer_name'].replace('.', '_'),
                            brickName.split(':')[1].replace('/', '|'),
                            fopStat.get('name')
                        )
                    ] = float(fopStat.get('hits'))
                    t_name = "clusters.%s.nodes.%s.bricks.%s.fop." \
                        "%s.latencyAvg"
                    ret_val[
                        t_name % (
                            CONFIG['integration_id'],
                            CONFIG['peer_name'].replace('.', '_'),
                            brickName.split(':')[1].replace('/', '|'),
                            fopStat.get('name')
                        )
                    ] = float(fopStat.get('latencyAvg'))
                    t_name = "clusters.%s.nodes.%s.bricks.%s.fop." \
                        "%s.latencyMin"
                    ret_val[
                        t_name % (
                            CONFIG['integration_id'],
                            CONFIG['peer_name'].replace('.', '_'),
                            brickName.split(':')[1].replace('/', '|'),
                            fopStat.get('name')
                        )
                    ] = float(fopStat.get('latencyMin'))
                    t_name = "clusters.%s.nodes.%s.bricks.%s.fop." \
                        "%s.latencyMax"
                    ret_val[
                        t_name % (
                            CONFIG['integration_id'],
                            CONFIG['peer_name'].replace('.', '_'),
                            brickName.split(':')[1].replace('/', '|'),
                            fopStat.get('name')
                        )
                    ] = float(fopStat.get('latencyMax'))
                    if fopStat.get('name') in READ_WRITE_OPS:
                        read_write_hits = read_write_hits + float(
                            fopStat.get('hits')
                        )
                    if fopStat.get('name') in LOCK_OPS:
                        lock_hits = lock_hits + float(fopStat.get('hits'))
                    if fopStat.get('name') in INODE_OPS:
                        inode_hits = inode_hits + float(fopStat.get('hits'))
                    if fopStat.get('name') in ENTRY_OPS:
                        entry_hits = entry_hits + float(fopStat.get('hits'))
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                    "read_write_ops"
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        volName,
                        CONFIG['peer_name'].replace('.', '_'),
                        brickName.split(':')[1].replace('/', '|')
                    )
                ] = read_write_hits
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                    "lock_ops"
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        volName,
                        CONFIG['peer_name'].replace('.', '_'),
                        brickName.split(':')[1].replace('/', '|')
                    )
                ] = lock_hits
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                    "inode_ops"
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        volName,
                        CONFIG['peer_name'].replace('.', '_'),
                        brickName.split(':')[1].replace('/', '|')
                    )
                ] = inode_hits
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                    "entry_ops"
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        volName,
                        CONFIG['peer_name'].replace('.', '_'),
                        brickName.split(':')[1].replace('/', '|')
                    )
                ] = entry_hits
                t_name = "clusters.%s.nodes.%s.bricks.%s." \
                    "read_write_ops"
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        CONFIG['peer_name'].replace('.', '_'),
                        brickName.split(':')[1].replace('/', '|')
                    )
                ] = read_write_hits
                t_name = "clusters.%s.nodes.%s.bricks.%s." \
                    "lock_ops"
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        CONFIG['peer_name'].replace('.', '_'),
                        brickName.split(':')[1].replace('/', '|')
                    )
                ] = lock_hits
                t_name = "clusters.%s.nodes.%s.bricks.%s." \
                    "inode_ops"
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        CONFIG['peer_name'].replace('.', '_'),
                        brickName.split(':')[1].replace('/', '|')
                    )
                ] = inode_hits
                t_name = "clusters.%s.nodes.%s.bricks.%s." \
                    "entry_ops"
                ret_val[
                    t_name % (
                        CONFIG['integration_id'],
                        CONFIG['peer_name'].replace('.', '_'),
                        brickName.split(':')[1].replace('/', '|')
                    )
                ] = entry_hits
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
                value = float(value)
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
