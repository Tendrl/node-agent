import collectd
import os
import shlex
import socket
import subprocess
from subprocess import Popen
import sys
import traceback


sys.path.append('/usr/lib64/collectd/gluster')
import utils as tendrl_glusterfs_utils
sys.path.remove('/usr/lib64/collectd/gluster')


CONFIG = {}
CLUSTER_TOPOLOGY = {}


def _get_mount_point(path):
    mount = os.path.realpath(path)
    while not os.path.ismount(mount):
        mount = os.path.dirname(mount)
    return mount


def _parse_proc_mounts(filter=True):
    mount_points = {}
    with open('/proc/mounts', 'r') as f:
        for line in f:
            if line.startswith("/") or not filter:
                mount = {}
                tokens = line.split()
                mount['device'] = tokens[0]
                mount['fsType'] = tokens[2]
                mount['mountOptions'] = tokens[3]
                mount_points[tokens[1]] = mount
    return mount_points


def _get_stats(mount_point):
    data = os.statvfs(mount_point)
    total = (data.f_blocks * data.f_bsize)
    free = (data.f_bfree * data.f_bsize)
    used_percent = 100 - (100.0 * free / total)
    total_inode = data.f_files
    free_inode = data.f_ffree
    used_percent_inode = 100 - (100.0 * free_inode / total_inode)
    used = total - free
    used_inode = total_inode - free_inode
    return {'total': total,
            'free': free,
            'used_percent': used_percent,
            'total_inode': total_inode,
            'free_inode': free_inode,
            'used_inode': used_inode,
            'used': used,
            'used_percent_inode': used_percent_inode}


def get_lvs():
    _lvm_cmd = (
        "lvm vgs --unquoted --noheading --nameprefixes "
        "--separator $ --nosuffix --units m -o lv_uuid,"
        "lv_name,data_percent,pool_lv,lv_attr,lv_size,"
        "lv_path,lv_metadata_size,metadata_percent,vg_name"
    )
    try:
        cmd = Popen(
            shlex.split(
                _lvm_cmd
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=open(os.devnull, "r"),
            close_fds=True
        )
        stdout, stderr = cmd.communicate()
        if stderr:
            collectd.error(
                'Failed to fetch lvs. Error %s' % stderr
            )
        else:
            out = stdout.split('\n')[:-1]
            l = map(
                lambda x: dict(x), map(
                    lambda x: [
                        e.split('=') for e in x
                    ],
                    map(lambda x: x.strip().split('$'), out)
                )
            )
            d = {}
            for i in l:
                if i['LVM2_LV_ATTR'][0] == 't':
                    k = "%s/%s" % (i['LVM2_VG_NAME'], i['LVM2_LV_NAME'])
                else:
                    k = os.path.realpath(i['LVM2_LV_PATH'])
                d.update({k: i})
            return d
    except (
        OSError,
        ValueError,
        KeyError,
        subprocess.CalledProcessError
    ) as ex:
        collectd.error('Failed to fetch lvs. Error %s' % str(ex))
        return None


def get_mount_stats(
    mount_path
):
    def _get_mounts(mount_path=[]):
        mount_list = _get_mount_point(mount_path)
        mount_points = _parse_proc_mounts()
        if isinstance(mount_list, basestring):
            mount_list = [mount_list]
        outList = set(mount_points).intersection(set(mount_list))
        # list comprehension to build dictionary does not work in
        # python 2.6.6
        mounts = {}
        for k in outList:
            mounts[k] = mount_points[k]
        return mounts

    def _get_thin_pool_stat(device):
        out = {'thinpool_size': None,
               'thinpool_used_percent': None,
               'metadata_size': None,
               'metadata_used_percent': None,
               'thinpool_free': None,
               'metadata_free': None,
               'thinpool_used': None,
               'metadata_used': None}
        if lvs and device in lvs and \
           lvs[device]['LVM2_LV_ATTR'][0] == 'V':
            thinpool = "%s/%s" % (lvs[device]['LVM2_VG_NAME'],
                                  lvs[device]['LVM2_POOL_LV'])
            out['thinpool_size'] = float(
                lvs[thinpool]['LVM2_LV_SIZE']) / 1024
            out['thinpool_used_percent'] = float(
                lvs[thinpool]['LVM2_DATA_PERCENT'])
            out['metadata_size'] = float(
                lvs[thinpool]['LVM2_LV_METADATA_SIZE']) / 1024
            out['metadata_used_percent'] = float(
                lvs[thinpool]['LVM2_METADATA_PERCENT'])
            out['thinpool_free'] = out['thinpool_size'] * (
                1 - out['thinpool_used_percent'] / 100.0)
            out['thinpool_used'] = \
                out['thinpool_size'] - out['thinpool_free']
            out['metadata_free'] = out['metadata_size'] * (
                1 - out['metadata_used_percent'] / 100.0)
            out['metadata_used'] = \
                out['metadata_size'] - out['metadata_free']
        return out
    mount_points = _get_mounts(mount_path)
    lvs = get_lvs()
    mount_detail = {}
    if not mount_points:
        return mount_detail
    for mount, info in mount_points.iteritems():
        mount_detail[mount] = _get_stats(mount)
        mount_detail[mount].update(
            _get_thin_pool_stat(os.path.realpath(info['device']))
        )
        mount_detail[mount].update({'mount_point': mount})
    return mount_detail


def brick_utilization(path):
    """{

         'used_percent': 0.6338674168297445,

         'used': 0.0316314697265625,

         'free_inode': 2621390,

         'used_inode': 50,

         'free': 4.9586029052734375,

         'total_inode': 2621440,

         'mount_point': u'/bricks/brick2',

         'metadata_used_percent': None,

         'total': 4.990234375,

         'thinpool_free': None,

         'metadata_used': None,

         'thinpool_used_percent': None,

         'used_percent_inode': 0.0019073486328125,

         'thinpool_used': None,

         'metadata_size': None,

         'metadata_free': None,

         'thinpool_size': None

    }
    """
    # Below logic will find mount_path from path
    mount_stats = get_mount_stats(path)
    if not mount_stats:
        return None
    return mount_stats.values()[0]


def get_brick_utilization():
    global CLUSTER_TOPOLOGY
    global CONFIG
    ret_val = {}
    volumes = CLUSTER_TOPOLOGY.get('volumes', [])
    for volume in volumes:
        utilizations = []
        for sub_volume_index, sub_volume_bricks in volume.get(
            'bricks',
            {}
        ).iteritems():
            for brick in sub_volume_bricks:
                brick_path = brick['path']
                brick_hostname = brick['hostname']
                # Check if current brick is from localhost else utilization
                # of brick from some other host can't be computed here..
                if (
                    brick_hostname == socket.gethostbyname(
                        CONFIG['peer_name']
                    ) or
                    brick_hostname == CONFIG['peer_name']
                ):
                    try:
                        utilization = brick_utilization(
                            brick['path']
                        )
                    except (
                        AttributeError,
                        KeyError,
                        ValueError
                    ):
                        collectd.error(
                            'Failed to fetch utilization of brick %s of host'
                            ' %s. Error %s' % (
                                brick['path'],
                                brick['hostname'],
                                traceback.format_exc()
                            )
                        )
                    if not utilization:
                        continue
                    utilization['hostname'] = brick_hostname
                    utilization['brick_path'] = brick_path
                    utilizations.append(utilization)
                ret_val[volume['name']] = utilizations
    return ret_val


def get_metrics():
    global CONFIG
    ret_val = {}
    stats = get_brick_utilization()
    for vol, brick_usages in stats.iteritems():
        for brick_usage in brick_usages:
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                "utilization.gauge-used"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    vol,
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('used')
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                "utilization.gauge-total"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    vol,
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('total')
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                "utilization.percent-percent_bytes"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    vol,
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('used_percent')
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                "thin_pool_utilization.percent-percent_bytes"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    vol,
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('thinpool_used_percent')
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s" \
                ".thin_pool_meta_data_utilization.percent-percent_bytes"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    vol,
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('metadata_used_percent')
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                "thin_pool_meta_data_utilization.gauge-used"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    vol,
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('metadata_used')
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                "inode_utilization.gauge-used"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    vol,
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('used_inode')
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                "inode_utilization.gauge-total"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    vol,
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('total_inode')
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                "inode_utilization.percent-percent_bytes"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    vol,
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('used_percent_inode')
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                "thin_pool_utilization.gauge-used"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    vol,
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('thinpool_used')
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                "thin_pool_utilization.gauge-total"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    vol,
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('thinpool_size')
            t_name = "clusters.%s.nodes.%s.bricks.%s.utilization." \
                "gauge-used"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('used')
            t_name = "clusters.%s.nodes.%s.bricks.%s.utilization." \
                "gauge-total"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('total')
            t_name = "clusters.%s.nodes.%s.bricks.%s.utilization." \
                "percent-percent_bytes"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('used_percent')
            t_name = "clusters.%s.nodes.%s.bricks.%s." \
                "thin_pool_utilization.percent-percent_bytes"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('thinpool_used_percent')
            t_name = "clusters.%s.nodes.%s.bricks.%s." \
                "thin_pool_meta_data_utilization.percent-percent_bytes"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('metadata_used_percent')
            t_name = "clusters.%s.nodes.%s.bricks.%s." \
                "thin_pool_meta_data_utilization.gauge-used"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('metadata_used')
            t_name = "clusters.%s.nodes.%s.bricks.%s.inode_utilization." \
                "gauge-used"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('used_inode')
            t_name = "clusters.%s.nodes.%s.bricks.%s.inode_utilization." \
                "gauge-total"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('total_inode')
            t_name = "clusters.%s.nodes.%s.bricks.%s.inode_utilization." \
                "percent-percent_bytes"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('used_percent_inode')
            t_name = "clusters.%s.nodes.%s.bricks.%s." \
                "thin_pool_utilization.gauge-used"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('thinpool_used')
            t_name = "clusters.%s.nodes.%s.bricks.%s." \
                "thin_pool_utilization.gauge-total"
            ret_val[
                t_name % (
                    CONFIG['integration_id'],
                    CONFIG['peer_name'].replace(".", "_"),
                    brick_usage.get('brick_path').replace("/", "|")
                )
            ] = brick_usage.get('thinpool_size')
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
