import ConfigParser
from gevent import socket
import os
import shlex
import subprocess
from subprocess import Popen
import time
import traceback
import uuid

import collectd


from tendrl.commons.utils import ini2json


GLUSTERD_ERROR_MSG = 'Connection failed. '\
    'Please check if gluster daemon is operational.'


def get_brick_state_mapping(status):
    return {
        'Started': 0,
        'Stopped': 2
    }.get(status, 1)


def get_tendrl_volume_status(status):
    return {
        'Created': 'Stopped'
    }.get(status, status)


def get_volume_state_mapping(status):
    return {
        'Started': 0,
        'Stopped': 2,
        'Created': 2
    }.get(status, 1)


def exec_command(cmd_str):
    try:
        cmd = Popen(
            shlex.split(
                cmd_str
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=open(os.devnull, "r"),
            close_fds=True
        )
        stdout, stderr = cmd.communicate()
        if stderr:
            return None, stderr
        return stdout, None
    except (subprocess.CalledProcessError, ValueError):
        except_traceback = traceback.format_exc()
        return None, except_traceback


def get_gluster_state_dump():
    global GLUSTERD_ERROR_MSG
    ret_val = {}
    try:
        file_name = "collectd_gstate_%s" % str(uuid.uuid4())
        gluster_state_dump_op, gluster_state_dump_err = exec_command(
            'gluster get-state glusterd odir /var/run file %s detail' % (
                file_name
            )
        )
        if (
            gluster_state_dump_err or
            GLUSTERD_ERROR_MSG in gluster_state_dump_op
        ):
            return ret_val, gluster_state_dump_err
        gluster_state_dump = ini2json.ini_to_dict(
            '/var/run/%s' % file_name
        )
        rm_state_dump, rm_state_dump_err = exec_command(
            'rm -rf /var/run/%s' % file_name
        )
        if rm_state_dump_err:
            return ret_val, rm_state_dump_err
        return gluster_state_dump, None
    except (
        IOError,
        AttributeError,
        ConfigParser.MissingSectionHeaderError,
        ConfigParser.ParsingError,
        ValueError
    ):
        return ret_val, traceback.format_exc()


def parse_get_state(get_state_json):
    cluster_topology = {}
    if "Peers" in get_state_json:
        cluster_peers = []
        processed_peer_indexes = []
        peers = get_state_json['Peers']
        for key, value in peers.iteritems():
            peer_index = key.split('.')[0].split('peer')[1]
            if peer_index not in processed_peer_indexes:
                cluster_peers.append({
                    'host_name': peers[
                        'peer%s.primary_hostname' % peer_index
                    ],
                    'uuid': peers[
                        'peer%s.uuid' % peer_index
                    ],
                    'state': peers[
                        'peer%s.state' % peer_index
                    ],
                    'connected': peers[
                        'peer%s.connected' % peer_index
                    ]
                })
                processed_peer_indexes.append(peer_index)
                cluster_topology['peers'] = cluster_peers
    if "Volumes" in get_state_json:
        processed_vol_indexes = []
        vols = []
        volumes = get_state_json['Volumes']
        for key, value in volumes.iteritems():
            vol_index = key.split('.')[0].split('volume')[1]
            if vol_index not in processed_vol_indexes:
                volume = {
                    'name': volumes['volume%s.name' % vol_index],
                    'id': volumes['volume%s.id' % vol_index],
                    'type': volumes['volume%s.type' % vol_index],
                    'transport_type': volumes[
                        'volume%s.transport_type' % vol_index
                    ],
                    'status': volumes['volume%s.status' % vol_index],
                    'brick_count': volumes['volume%s.brickcount' % vol_index],
                    'snap_count': volumes['volume%s.snap_count' % vol_index],
                    'stripe_count': volumes[
                        'volume%s.stripe_count' % vol_index
                    ],
                    'replica_count': volumes[
                        'volume%s.replica_count' % vol_index
                    ],
                    'subvol_count': volumes[
                        'volume%s.subvol_count' % vol_index
                    ],
                    'arbiter_count': volumes[
                        'volume%s.arbiter_count' % vol_index
                    ],
                    'disperse_count': volumes[
                        'volume%s.disperse_count' % vol_index
                    ],
                    'redundancy_count': volumes[
                        'volume%s.redundancy_count' % vol_index
                    ],
                    'quorum_status': volumes[
                        'volume%s.quorum_status' % vol_index
                    ],
                    'rebalance_status': volumes[
                        'volume%s.rebalance.status' % vol_index
                    ],
                    'rebalance_failures': volumes[
                        'volume%s.rebalance.failures' % vol_index
                    ],
                    'rebalance_skipped': volumes[
                        'volume%s.rebalance.skipped' % vol_index
                    ],
                    'rebalance_files': volumes[
                        'volume%s.rebalance.files' % vol_index
                    ],
                    'rebalance_data': volumes[
                        'volume%s.rebalance.data' % vol_index
                    ]
                }
                sub_volumes = {}
                no_of_bricks = int(volume['brick_count'])
                for brick_index in range(1, no_of_bricks + 1):
                    client_count = 0
                    if (
                        'volume%s.brick%s.client_count' % (
                            vol_index,
                            brick_index
                        ) in volumes
                    ):
                        client_count = volumes[
                            'volume%s.brick%s.client_count' % (
                                vol_index,
                                brick_index
                            )
                        ]
                    brick = {
                        'hostname': volumes[
                            'volume%s.brick%s.hostname' % (
                                vol_index,
                                brick_index
                            )
                        ],
                        'path': volumes[
                            'volume%s.brick%s.path' % (
                                vol_index,
                                brick_index
                            )
                        ].split(':')[1],
                        'connections_count': client_count
                    }
                    brick_status_key = 'volume%s.brick%s.status' % (
                        vol_index,
                        brick_index
                    )
                    if brick_status_key in volumes:
                        brick['status'] = volumes[brick_status_key]
                    sub_vol_index = (
                        (brick_index - 1) * int(volume['subvol_count'])
                    ) / no_of_bricks
                    sub_vol_bricks = sub_volumes.get(str(sub_vol_index), [])
                    sub_vol_bricks.append(brick)
                    sub_volumes[str(sub_vol_index)] = sub_vol_bricks
                volume['bricks'] = sub_volumes
                vols.append(volume)
                cluster_topology['volumes'] = vols
                processed_vol_indexes.append(vol_index)
    return cluster_topology


def get_gluster_cluster_topology():
    gluster_state_dump_json, gluster_state_dump_err = get_gluster_state_dump()
    if gluster_state_dump_err:
        collectd.error(
            'Failed to fetch cluster topology. Error %s' % (
                gluster_state_dump_err
            )
        )
        return {}
    try:
        cluster_topology = parse_get_state(
            gluster_state_dump_json
        )
        return cluster_topology
    except (KeyError, AttributeError):
        collectd.error(
            'Failed to fetch cluster topology. Error %s' % (
                traceback.format_exc()
            )
        )
        return {}


# The below along with write_graphite function have to go into a custom
# write plugin to overcome shortcomings of write_graphite plugin
# And calls to write_grapite have to be replaced with collectd#Values
# i.e, send_metric need to be used..
prefix = 'tendrl'
delimeter = '.'


def write_graphite(path, value, graphite_host, graphite_port):
    try:
        graphite_sock = socket.socket()
        graphite_sock.connect(
            (
                graphite_host,
                int(graphite_port)
            )
        )
        message = '%s%s%s %s %d\n' % (
            prefix,
            delimeter,
            path,
            str(value),
            int(time.time())
        )
        graphite_sock.sendall(message)
        graphite_sock.close()
    except (
        socket.error,
        socket.gaierror
    ):
        collectd.error(
            'Failed to push brick stat for %s.Error %s' % (
                path,
                traceback.format_exc()
            )
        )


def send_metric(
    plugin_name,
    metric_type,
    instance_name,
    value,
    integration_id,
    plugin_instance=None
):
    metric = collectd.Values()
    metric.plugin = plugin_name
    metric.host = "cluster_%s" % integration_id
    metric.type = metric_type
    metric.values = [value]
    metric.type_instance = instance_name
    if plugin_instance:
        metric.plugin_instance = plugin_instance
    metric.dispatch()
