#!/usr/bin/python

import collectd
import json
import os
import subprocess

PLUGIN_NAME = 'cluster_utilization'
CONFIG = None


def configure_callback(configobj):
    global CONFIG
    CONFIG = {
        c.key: c.values[0] for c in configobj.children
    }


def _idx_in_list(list, str):
        idx = -1
        for item in list:
            idx += 1
            if item == str:
                return idx
        return -1


def _to_bytes(str):
    if str.endswith('K') or str.endswith('k'):
        return int(str[:-1]) * 1024
    if str.endswith('M') or str.endswith('m'):
        return int(str[:-1]) * 1024 * 1024
    if str.endswith('G') or str.endswith('g'):
        return int(str[:-1]) * 1024 * 1024 * 1024
    if str.endswith('T') or str.endswith('t'):
        return int(str[:-1]) * 1024 * 1024 * 1024 * 1024
    if str.endswith('P') or str.endswith('p'):
        return int(str[:-1]) * 1024 * 1024 * 1024 * 1024 * 1024
    return int(str)


def fetch_cluster_and_pool_utilization(cluster_name):
    args = ['ceph', 'df', '--cluster', cluster_name]
    cluster_stat = {}
    pool_stat = []
    p = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=open(os.devnull, "r"),
        close_fds=True
    )
    stdout, stderr = p.communicate()
    stdout = stdout.replace('RAW USED', 'RAW_USED')
    stdout = stdout.replace('%RAW USED', '%RAW_USED')
    stdout = stdout.replace('MAX AVAIL', 'MAX_AVAIL')
    lines = stdout.split('\n')
    index = 0
    pool_stat_available = False
    while index < len(lines):
        line = lines[index]
        if line == "" or line == '\n':
            index += 1
            continue
        if "GLOBAL" in line:
            index += 1
            if len(lines) < 3:
                return (
                    cluster_stat,
                    pool_stat,
                    "Failed to parse pool stats data"
                )
            cluster_fields = lines[index].split()
            cluster_size_idx = _idx_in_list(
                cluster_fields,
                'SIZE'
            )
            cluster_avail_idx = _idx_in_list(
                cluster_fields,
                'AVAIL'
            )
            cluster_used_idx = _idx_in_list(
                cluster_fields,
                'RAW_USED'
            )
            cluster_pcnt_used_idx = _idx_in_list(
                cluster_fields,
                '%RAW_USED'
            )
            if cluster_size_idx == -1 or cluster_avail_idx == -1 or \
                    cluster_used_idx == -1 or cluster_pcnt_used_idx == -1:
                return (
                    cluster_stat,
                    pool_stat,
                    "Missing fields in cluster stat"
                )
            index += 1
            if index >= len(lines):
                return (
                    cluster_stat,
                    pool_stat,
                    "No cluster stats to parse"
                )
            line = lines[index]
            cluster_fields = line.split()
            if len(cluster_fields) < 4:
                return (
                    cluster_stat,
                    pool_stat,
                    "Missing fields in cluster stat"
                )
            cluster_stat['total'] = _to_bytes(
                cluster_fields[cluster_size_idx]
            )
            cluster_stat['used'] = _to_bytes(
                cluster_fields[cluster_used_idx]
            )
            cluster_stat['available'] = _to_bytes(
                cluster_fields[cluster_avail_idx]
            )
            cluster_stat['pcnt_used'] = cluster_fields[
                cluster_pcnt_used_idx
            ]
        if "POOLS" in line:
            pool_stat_available = True
            index += 1
            if index >= len(lines):
                return (cluster_stat, pool_stat, '')
            pool_fields = lines[index].split()
            pool_name_idx = _idx_in_list(pool_fields, 'NAME')
            pool_id_idx = _idx_in_list(pool_fields, 'ID')
            pool_used_idx = _idx_in_list(pool_fields, 'USED')
            pool_pcnt_used_idx = _idx_in_list(
                pool_fields,
                '%USED'
            )
            pool_max_avail_idx = _idx_in_list(
                pool_fields,
                'MAX_AVAIL'
            )
            if pool_name_idx == -1 or pool_id_idx == -1 or \
                    pool_used_idx == -1 or pool_pcnt_used_idx == -1 or \
                    pool_max_avail_idx == -1:
                return (cluster_stat, pool_stat, '')
            index += 1
        if pool_stat_available is True:
            line = lines[index]
            pool_fields = line.split()
            if len(pool_fields) < 5:
                return (cluster_stat, pool_stat, '')
            dict = {}
            dict['name'] = pool_fields[pool_name_idx]
            dict['available'] = _to_bytes(
                pool_fields[pool_max_avail_idx]
            )
            dict['used'] = _to_bytes(
                pool_fields[pool_used_idx]
            )
            dict['pcnt_used'] = pool_fields[pool_pcnt_used_idx]
            pool_stat.append(dict)
        index += 1
    return (cluster_stat, pool_stat, '')


def fetch_osd_utilization(cluster_name):
    args = ['ceph', 'osd', 'df', '--cluster', cluster_name, '-f', 'json']
    p = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=open(os.devnull, "r"),
        close_fds=True
    )
    stdout, stderr = p.communicate()
    if stderr == "" and p.returncode == 0:
        result = json.loads(stdout)
    return (result, stderr)


def fetch_rbd_utilizations(cluster_name, pools):
    rbd_stats = []
    for pool in pools:
        args = [
            'rbd',
            'du',
            '--cluster',
            cluster_name,
            '-p',
            pool,
            '--format',
            'json'
        ]
        try:
            p = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=open(os.devnull, "r"),
                close_fds=True
            )
            stdout, stderr = p.communicate()
            if stderr == "" and p.returncode == 0:
                rbds = json.loads(stdout).get('images', {})
                rbd_stats.append({
                    'pool_name': pool,
                    'rbds': rbds
                })
            else:
                collectd.error(
                    "Failed to fetch rbd utilizations."
                    " The error is %s" % (
                        stderr
                    )
                )
        except (
            OSError,
            ValueError,
            KeyError,
            subprocess.CalledProcessError
        ) as e:
            collectd.error(
                "Failed to fetch osd utilizations."
                " The error is %s" % (
                    str(e)
                )
            )
            continue
    return rbd_stats


def send_metric(
    plugin_name,
    metric_type,
    instance_name,
    value,
    plugin_instance=None
):
    global CONFIG
    metric = collectd.Values()
    metric.plugin = plugin_name
    metric.host = "cluster_%s" % CONFIG['integration_id']
    metric.type = metric_type
    metric.values = [value]
    metric.type_instance = instance_name
    if plugin_instance:
        metric.plugin_instance = plugin_instance
    metric.dispatch()


def read_callback(data=None):
    global CONFIG
    try:
        cluster_stats, pools_stats, err = fetch_cluster_and_pool_utilization(
            CONFIG['cluster_name']
        )
        if err:
            collectd.error(
                "Failed to fetch cluster and pool utilizations"
                " The error is %s" % (
                    err
                )
            )
        else:
            pools = []
            if cluster_stats:
                send_metric(
                    'cluster_utilization',
                    'gauge',
                    'total',
                    cluster_stats.get('total')
                )
                send_metric(
                    'cluster_utilization',
                    'gauge',
                    'used',
                    cluster_stats.get('used')
                )
                send_metric(
                    'cluster_utilization',
                    'percent',
                    'percent_bytes',
                    float(cluster_stats.get('pcnt_used'))
                )
            for pool_stat in pools_stats:
                pools.append(pool_stat.get('name'))
                send_metric(
                    'pool_utilization',
                    'gauge',
                    'free',
                    pool_stat.get('available'),
                    plugin_instance=pool_stat.get('name')
                )
                send_metric(
                    'pool_utilization',
                    'gauge',
                    'used',
                    pool_stat.get('used'),
                    plugin_instance=pool_stat.get('name')
                )
                send_metric(
                    'pool_utilization',
                    'percent',
                    'percent_bytes',
                    float(pool_stat.get('pcnt_used')),
                    plugin_instance=pool_stat.get('name')
                )
    except (
        OSError,
        ValueError,
        KeyError,
        subprocess.CalledProcessError
    ) as ex:
        collectd.error(
            "Failed to fetch cluster and pool utilizations"
            " The error is %s" % (
                str(ex)
            )
        )
    try:
        osd_utilizations, err = fetch_osd_utilization(CONFIG['cluster_name'])
        if err:
            collectd.error(
                "Failed to fetch osd utilizations"
                " The error is %s" % (
                    err
                )
            )
        else:
            for osd_utilization in osd_utilizations['nodes']:
                send_metric(
                    'osd_utilization',
                    'gauge',
                    'free',
                    osd_utilization.get('kb_avail') * 1024,
                    plugin_instance=osd_utilization.get('name').replace(
                        '.',
                        '_'
                    )
                )
                send_metric(
                    'osd_utilization',
                    'gauge',
                    'total',
                    osd_utilization.get('kb') * 1024,
                    plugin_instance=osd_utilization.get('name').replace(
                        '.',
                        '_'
                    )
                )
                send_metric(
                    'osd_utilization',
                    'percent',
                    'percent_bytes',
                    float(osd_utilization.get('utilization')),
                    plugin_instance=osd_utilization.get('name').replace(
                        '.',
                        '_'
                    )
                )
                send_metric(
                    'osd_utilization',
                    'gauge',
                    'used',
                    osd_utilization.get('kb_used') * 1024,
                    plugin_instance=osd_utilization.get('name').replace(
                        '.',
                        '_'
                    )
                )
    except (
        OSError,
        ValueError,
        KeyError,
        subprocess.CalledProcessError
    ) as ex:
        collectd.error(
            "Failed to fetch osd utilizations"
            " The error is %s" % (
                str(ex)
            )
        )
    rbd_utilizations = fetch_rbd_utilizations(
        CONFIG['cluster_name'],
        pools
    )
    for rbd_utilization in rbd_utilizations:
        pool_name = rbd_utilization.get('pool_name', '').replace('.', '_')
        for rbd in rbd_utilization.get('rbds', []):
            rbd_name = rbd.get('name').replace('.', '_')
            send_metric(
                'rbd_utilization',
                'gauge',
                'total',
                rbd.get('provisioned_size'),
                plugin_instance='pool_%s|name_%s' % (pool_name, rbd_name)
            )
            send_metric(
                'rbd_utilization',
                'gauge',
                'used',
                rbd.get('used_size'),
                plugin_instance='pool_%s|name_%s' % (pool_name, rbd_name)
            )
            if rbd.get('provisioned_size') > 0:
                send_metric(
                    'rbd_utilization',
                    'percent',
                    'percent_bytes',
                    float((
                        rbd.get('used_size') * 100 * 1.0
                    ) / (
                        rbd.get('provisioned_size') * 1.0
                    )),
                    plugin_instance='pool_%s|name_%s' % (
                        pool_name,
                        rbd_name
                    )
                )


collectd.register_config(configure_callback)
collectd.register_read(read_callback, 60)
