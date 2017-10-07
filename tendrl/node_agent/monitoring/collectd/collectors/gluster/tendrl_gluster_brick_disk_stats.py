import ast
import etcd
import psutil
import re
import socket
import threading
import time
import traceback


import collectd
import utils as gluster_utils


class TendrlBrickDeviceStatsPlugin(object):
    CONFIG = {}
    etcd_client = {}

    def __init__(self):
        self.provisioner_only_plugin = False
        self.STAT_INTERVAL_FOR_PER_SEC_COUNTER = 10
        self.brick_details = {}
        if not self.etcd_client:
            _etcd_args = dict(
                host=self.CONFIG['etcd_host'],
                port=int(self.CONFIG['etcd_port'])
            )
            etcd_ca_cert_file = self.CONFIG.get("etcd_ca_cert_file")
            etcd_cert_file = self.CONFIG.get("etcd_ert_file")
            etcd_key_file = self.CONFIG.get("etcd_key_file")
            if (
                etcd_ca_cert_file and
                str(etcd_ca_cert_file) != "" and
                etcd_cert_file and
                str(etcd_cert_file) != "" and
                etcd_key_file and
                str(etcd_key_file) != ""
            ):
                _etcd_args.update(
                    {
                        "ca_cert": str(self.CONFIG['etcd_ca_cert_file']),
                        "cert": (
                            str(self.CONFIG['etcd_cert_file']),
                            str(self.CONFIG['etcd_key_file'])
                        ),
                        "protocol": "https"
                    }
                )
            self.etcd_client = etcd.Client(**_etcd_args)

    def fetch_brick_devices(self, brick_path):
        mount_point = self.get_brick_source_and_mount(
            brick_path
        )
        try:
            brick_devices = ast.literal_eval(
                self.etcd_client.read(
                    '/clusters/%s/Bricks/all/%s/%s/devices' % (
                        self.CONFIG['integration_id'],
                        self.CONFIG['peer_name'],
                        brick_path.replace('/', '_').replace("_", "", 1)
                    )
                ).value
            )
            brick_device_partitions = ast.literal_eval(
                self.etcd_client.read(
                    '/clusters/%s/Bricks/all/%s/%s/partitions' % (
                        self.CONFIG['integration_id'],
                        self.CONFIG['peer_name'],
                        brick_path.replace('/', '_').replace("_", "", 1)
                    )
                ).value
            )
            return brick_devices, brick_device_partitions, mount_point
        except etcd.EtcdKeyNotFound:
            return [], [], mount_point

    def get_brick_source_and_mount(self, brick_path):
        # source and target correspond to fields "Filesystem" and
        # "Mounted on" from df command output. The below command
        # gives the filesystem and mount point for a given path,
        # Eg: "/dev/mapper/tendrlMyBrick4_vg-tendrlMyBrick4_lv " \
        #     "/tendrl_gluster_bricks/MyBrick4_mount"

        command = "df --output=source,target " + brick_path
        out, err = gluster_utils.exec_command(command)
        if err:
            return None
        mount_source, mount_point = out.split("\n")[-2].split()
        return mount_point

    def get_brick_devices(self, brick_path):
        try:
            return self.fetch_brick_devices(brick_path)
        except (etcd.EtcdConnectionFailed, etcd.EtcdException):
            self.etcd_client = None
            trial_cnt = 0
            while not self.etcd_client:
                trial_cnt = trial_cnt + 1
                try:
                    _etcd_args = dict(
                        host=self.CONFIG['etcd_host'],
                        port=int(self.CONFIG['etcd_port'])
                    )
                    etcd_ca_cert_file = self.CONFIG.get("etcd_ca_cert_file")
                    etcd_cert_file = self.CONFIG.get("etcd_ert_file")
                    etcd_key_file = self.CONFIG.get("etcd_key_file")
                    if (
                        etcd_ca_cert_file and
                        str(etcd_ca_cert_file) != "" and
                        etcd_cert_file and
                        str(etcd_cert_file) != "" and
                        etcd_key_file and
                        str(etcd_key_file) != ""
                    ):
                        _etcd_args.update(
                            {
                                "ca_cert": str(
                                    self.CONFIG['etcd_ca_cert_file']
                                ),
                                "cert": (
                                    str(self.CONFIG['etcd_cert_file']),
                                    str(self.CONFIG['etcd_key_file'])),
                                "protocol": "https"
                            }
                        )
                    self.etcd_client = etcd.Client(**_etcd_args)
                except etcd.EtcdException:
                    collectd.error(
                        "Error connecting to central store (etcd), trying "
                        "again..."
                    )
                    time.sleep(2)
                if trial_cnt == 3:
                    if not self.etcd_client:
                        return []
                    return self.fetch_brick_devices(brick_path)
            return self.fetch_brick_devices(brick_path)

    def get_interval_device_io_stat(self, device_name, attr_name):
        return (
            (
                getattr(self.current_io_stats[
                    device_name.replace(
                        '/dev/',
                        ''
                    )
                ], attr_name) -
                getattr(self.initial_io_stats[
                    device_name.replace(
                        '/dev/',
                        ''
                    )
                ], attr_name, 0)
            ) * 1.0
        ) / (self.STAT_INTERVAL_FOR_PER_SEC_COUNTER * 1.0)

    def get_interval_disk_io_stat(self, device_name, partitions, attr_name):
        if (
            device_name.replace('/dev/', '') in self.current_io_stats and
            device_name.replace('/dev/', '') in self.initial_io_stats
        ):
            return self.get_interval_device_io_stat(device_name, attr_name)
        else:
            # Use partitions
            sum = 0
            for partition in partitions:
                sum = sum + self.get_interval_device_io_stat(
                    partition,
                    attr_name
                )
            return sum

    def get_disk_usage(self, device_name):
        return psutil.disk_usage(device_name)

    def populate_disk_details(self, vol_name, brick_host, brick_path):
        try:
            device_to_partitions = {}
            brick_devices, brick_device_partitions, mount_point = \
                self.get_brick_devices(brick_path)
            if not (brick_devices or brick_device_partitions):
                collectd.error(
                    'Failed to fetch device details for brick %s:%s'
                    ' of volume %s' % (
                        brick_host,
                        brick_path,
                        vol_name
                    )
                )
                return
            for device in brick_devices:
                partition_name_re = re.compile('%s[0-9]+' % device)
                device_partitions = []
                for partition in brick_device_partitions:
                    if partition_name_re.match(partition):
                        device_partitions = device_to_partitions.get(
                            device,
                            []
                        )
                        device_partitions.append(partition)
                device_to_partitions[device] = device_partitions
            for brick_device, partitions in device_to_partitions.iteritems():
                # Collect disk read and write octets
                # Push to cluster->volume->node->brick tree
                self.brick_details[
                    'clusters.%s.volumes.%s.nodes.%s.bricks.%s.device.%s.'
                    'disk_octets.read' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = self.get_interval_disk_io_stat(
                    brick_device,
                    partitions,
                    'read_bytes'
                )
                self.brick_details[
                    'clusters.%s.volumes.%s.nodes.%s.bricks.%s.device.%s.'
                    'disk_octets.write' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = self.get_interval_disk_io_stat(
                    brick_device,
                    partitions,
                    'write_bytes'
                )
                # Push to cluster->node->brick tree
                self.brick_details[
                    'clusters.%s.nodes.%s.bricks.%s.device.%s.'
                    'disk_octets.read' % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = self.get_interval_disk_io_stat(
                    brick_device,
                    partitions,
                    'read_bytes'
                )
                self.brick_details[
                    'clusters.%s.nodes.%s.bricks.%s.device.%s.'
                    'disk_octets.write' % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = self.get_interval_disk_io_stat(
                    brick_device,
                    partitions,
                    'write_bytes'
                )
                # Collect disk read and write io
                # Push cluster->volume->host->brick tree
                self.brick_details[
                    'clusters.%s.volumes.%s.nodes.%s.bricks.%s.device.%s.'
                    'disk_ops.read' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = self.get_interval_disk_io_stat(
                    brick_device,
                    partitions,
                    'read_count'
                )
                self.brick_details[
                    'clusters.%s.volumes.%s.nodes.%s.bricks.%s.device.%s.'
                    'disk_ops.write' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = self.get_interval_disk_io_stat(
                    brick_device,
                    partitions,
                    'write_count'
                )
                # Push to cluster->node->brick tree
                self.brick_details[
                    'clusters.%s.nodes.%s.bricks.%s.device.%s.'
                    'disk_ops.read' % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = self.get_interval_disk_io_stat(
                    brick_device,
                    partitions,
                    'read_count'
                )
                self.brick_details[
                    'clusters.%s.nodes.%s.bricks.%s.device.%s.'
                    'disk_ops.write' % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = self.get_interval_disk_io_stat(
                    brick_device,
                    partitions,
                    'write_count'
                )
                # Collect disk read and write latency
                # Push to cluster->volume->node->brick tree
                self.brick_details[
                    'clusters.%s.volumes.%s.nodes.%s.bricks.%s.device.%s.'
                    'disk_time.read' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = self.get_interval_disk_io_stat(
                    brick_device,
                    partitions,
                    'read_time'
                )
                self.brick_details[
                    'clusters.%s.volumes.%s.nodes.%s.bricks.%s.device.%s.'
                    'disk_time.write' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = self.get_interval_disk_io_stat(
                    brick_device,
                    partitions,
                    'write_time'
                )
                # Push to cluster->node->brick tree
                self.brick_details[
                    'clusters.%s.nodes.%s.bricks.%s.device.%s.'
                    'disk_time.read' % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = self.get_interval_disk_io_stat(
                    brick_device,
                    partitions,
                    'read_time'
                )
                self.brick_details[
                    'clusters.%s.nodes.%s.bricks.%s.device.%s.'
                    'disk_time.write' % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = self.get_interval_disk_io_stat(
                    brick_device,
                    partitions,
                    'write_time'
                )
                # Collect disk utilization
                # Push to cluster->volume->node->brick tree
                disk_usage = self.get_disk_usage(brick_device)
                self.brick_details[
                    'clusters.%s.volumes.%s.nodes.%s.bricks.%s.device.%s.'
                    'utilization.used' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = disk_usage.used
                self.brick_details[
                    'clusters.%s.volumes.%s.nodes.%s.bricks.%s.device.%s.'
                    'utilization.total' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = disk_usage.total
                self.brick_details[
                    'clusters.%s.volumes.%s.nodes.%s.bricks.%s.device.%s.'
                    'utilization.percent_used' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = disk_usage.percent
                # Push to cluster->node->brick tree
                self.brick_details[
                    'clusters.%s.nodes.%s.bricks.%s.device.%s.'
                    'utilization.used' % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = disk_usage.used
                self.brick_details[
                    'clusters.%s.nodes.%s.bricks.%s.device.%s.'
                    'utilization.total' % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = disk_usage.total
                self.brick_details[
                    'clusters.%s.nodes.%s.bricks.%s.device.%s.'
                    'utilization.percent_used' % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = disk_usage.percent
                # Collect disk mount-point utilization
                if not mount_point:
                    return
                disk_usage = self.get_disk_usage(mount_point)
                self.brick_details[
                    'clusters.%s.volumes.%s.nodes.%s.bricks.%s.device.%s.'
                    'mount_utilization.used' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = disk_usage.used
                self.brick_details[
                    'clusters.%s.volumes.%s.nodes.%s.bricks.%s.device.%s.'
                    'mount_utilization.total' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = disk_usage.total
                self.brick_details[
                    'clusters.%s.volumes.%s.nodes.%s.bricks.%s.device.%s.'
                    'mount_utilization.percent_used' % (
                        self.CONFIG['integration_id'],
                        vol_name,
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = disk_usage.percent
                # Push to cluster->node->brick tree
                self.brick_details[
                    'clusters.%s.nodes.%s.bricks.%s.device.%s.'
                    'mount_utilization.used' % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = disk_usage.used
                self.brick_details[
                    'clusters.%s.nodes.%s.bricks.%s.device.%s.'
                    'mount_utilization.total' % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = disk_usage.total
                self.brick_details[
                    'clusters.%s.nodes.%s.bricks.%s.device.%s.'
                    'mount_utilization.percent_used' % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brick_path.replace('/', '|'),
                        brick_device.replace('/dev/', '')
                    )
                ] = disk_usage.percent
        except (AttributeError, KeyError):
            collectd.error(
                'Failed to populate_disk_details for volume %s, brick %s.'
                'Error %s' % (
                    vol_name,
                    brick_path,
                    traceback.format_exc()
                )
            )

    def get_metrics(self):
        self.initial_io_stats = psutil.disk_io_counters(perdisk=True)
        curr_host_name = socket.gethostbyname(
            self.CONFIG['peer_name']
        )
        time.sleep(self.STAT_INTERVAL_FOR_PER_SEC_COUNTER)
        self.current_io_stats = psutil.disk_io_counters(perdisk=True)
        threads = []
        for volume in self.CLUSTER_TOPOLOGY.get('volumes', []):
            for sub_volume_index, sub_volume_bricks in volume.get(
                'bricks',
                []
            ).iteritems():
                for brick in sub_volume_bricks:
                    brick_hostname = brick['hostname']
                    if (
                        brick_hostname == curr_host_name or
                        brick_hostname == self.CONFIG['peer_name']
                    ):
                        thread = threading.Thread(
                            target=self.populate_disk_details,
                            args=(
                                volume['name'],
                                brick['hostname'],
                                brick['path'],
                            )
                        )
                        thread.start()
                        threads.append(
                            thread
                        )
        for thread in threads:
            thread.join(1)
        for thread in threads:
            del thread
        return self.brick_details


def r_callback():
    TendrlBrickDeviceStatsPlugin.CLUSTER_TOPOLOGY = \
        gluster_utils.get_gluster_cluster_topology()
    metrics = TendrlBrickDeviceStatsPlugin().get_metrics()
    for metric_name, value in metrics.iteritems():
        if value is not None:
            if (
                isinstance(value, str) and
                value.isdigit()
            ):
                value = int(value)
            gluster_utils.write_graphite(
                metric_name,
                value,
                TendrlBrickDeviceStatsPlugin.CONFIG['graphite_host'],
                TendrlBrickDeviceStatsPlugin.CONFIG['graphite_port']
            )


def configure_callback(configobj):
    TendrlBrickDeviceStatsPlugin.CONFIG = {
        c.key: c.values[0] for c in configobj.children
    }


collectd.register_config(configure_callback)
collectd.register_read(r_callback, 77)
