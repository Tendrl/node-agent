import psutil
import socket
import threading
import time
import traceback


import collectd
from tendrl_gluster import TendrlGlusterfsMonitoringBase
import utils as gluster_utils


class TendrlBrickDeviceStatsPlugin(
    TendrlGlusterfsMonitoringBase
):
    def __init__(self):
        self.provisioner_only_plugin = False
        TendrlGlusterfsMonitoringBase.__init__(self)
        self.STAT_INTERVAL_FOR_PER_SEC_COUNTER = 10
        self.brick_details = {}

    def get_brick_source_and_mount(self, brick_path):
        # source and target correspond to fields "Filesystem" and
        # "Mounted on" from df command output. The below command
        # gives the filesystem and mount point for a given path,
        # Eg: "/dev/mapper/tendrlMyBrick4_vg-tendrlMyBrick4_lv " \
        #     "/tendrl_gluster_bricks/MyBrick4_mount"

        command = "df --output=source,target " + brick_path
        out, err = gluster_utils.exec_command(command)
        if err:
            return None, None, err
        mount_source, mount_point = out.split("\n")[-2].split()
        return mount_source, mount_point, None

    def get_brick_devices(self, brick_path):
        mount_source, mount_point, err = self.get_brick_source_and_mount(
            brick_path
        )
        if err or (not mount_source or not mount_point):
            collectd.error(
                'mount_source is %s\n mount_point is %s\n DEVICE_TREE is %s\n'
                'Failed to fetch device details of brick %s.'
                'Error %s.' % (
                    str(mount_source),
                    str(mount_point),
                    str(self.DEVICE_TREE),
                    brick_path,
                    err
                )
            )
            return None, None
        device = self.DEVICE_TREE.resolveDevice(mount_source)
        disks = [
            d.path for d in device.ancestors if d.isDisk and not d.parents
        ]
        return disks, mount_point

    def get_interval_disk_io_stat(self, device_name, attr_name):
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
                ], attr_name)
            ) * 1.0
        ) / (self.STAT_INTERVAL_FOR_PER_SEC_COUNTER * 1.0)

    def get_disk_usage(self, device_name):
        return psutil.disk_usage(device_name)

    def populate_disk_details(self, vol_name, brick_host, brick_path):
        try:
            brick_devices, mount_point = self.get_brick_devices(brick_path)
            if not brick_devices:
                collectd.error(
                    'Failed to fetch device details for brick %s:%s'
                    ' of volume %s' % (
                        brick_host,
                        brick_path,
                        vol_name
                    )
                )
                return
            for brick_device in brick_devices:
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
