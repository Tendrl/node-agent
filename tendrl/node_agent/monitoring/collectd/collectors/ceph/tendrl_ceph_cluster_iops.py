#!/usr/bin/python

import collectd
import json
import os
import subprocess

CONFIG = None


def configure_callback(configobj):
    global CONFIG
    CONFIG = {
        c.key: c.values[0] for c in configobj.children
    }


def fetch_cluster_iops(cluster_name):
    args = [
        'ceph',
        'pg',
        'dump',
        'summary',
        '--cluster',
        cluster_name,
        '-f',
        'json'
    ]
    p = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=open(os.devnull, "r"),
        close_fds=True
    )
    stdout, stderr = p.communicate()
    if p.returncode == 0:
        result = json.loads(stdout)
        return (
            result['pg_stats_sum']['stat_sum']['num_read'],
            result['pg_stats_sum']['stat_sum']['num_write'],
            ''
        )
    else:
        return (0, 0, stderr)


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
        iops_read, iops_write, err = fetch_cluster_iops(CONFIG['cluster_name'])
        if err:
            collectd.error(
                "Failed to fetch cluster iops"
                " The error is %s" % (
                    err
                )
            )
            return
        send_metric(
            'cluster_iops_write',
            'gauge',
            'total',
            iops_write
        )
        send_metric(
            'cluster_iops_read',
            'gauge',
            'total',
            iops_read
        )
        send_metric(
            'cluster_iops_read_write',
            'gauge',
            'total',
            iops_read + iops_write
        )
    except (
        OSError,
        ValueError,
        KeyError,
        subprocess.CalledProcessError
    ) as ex:
        collectd.error(
            "Failed to fetch cluster iops"
            " The error is %s" % (
                str(ex)
            )
        )


collectd.register_config(configure_callback)
collectd.register_read(read_callback, 60)
