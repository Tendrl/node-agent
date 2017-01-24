from tendrl.commons.etcdobj import EtcdObj
from tendrl.node_agent import objects


class Disk(objects.NodeAgentBaseObject):
    def __init__(self, disk_id=None, device_name=None, disk_kernel_name=None,
                 parent_id=None, parent_name=None, disk_type=None, fsuuid=None,
                 mount_point=None, model=None, vendror=None, used=None,
                 serial_no=None, rmversion=None, fstype=None, ssd=None,
                 size=None, device_number=None, driver=None, group=None,
                 device=None, bios_id=None, state=None, driver_status=None,
                 label=None, req_queue_size=None, driver_mosules=None,
                 mode=None, owner=None, min_io_size=None,
                 major_to_minor_no=None, device_files=None, sysfs_busid=None,
                 alignment=None, read_only=None, read_ahead=None,
                 removable_device=None, scheduler_name=None, sysfs_id=None,
                 sysfs_device_link=None, geo_bios_edd=None,
                 geo_bios_legacy=None, geo_logical=None, phy_sector_size=None,
                 discard_granularity=None, discard_align_offset=None,
                 discard_max_bytes=None, discard_zeros_data=None,
                 optimal_io_size=None, log_sector_size=None, drive_status=None,
                 *args, **kwargs):
        super(Disk, self).__init__(*args, **kwargs)
        self.value = 'nodes/%s/Disks/%s'
        self.disk_id = disk_id
        self.device_name = device_name
        self.disk_kernel_name = disk_kernel_name
        self.parent_id = parent_id
        self.parent_name = parent_name
        self.disk_type = disk_type
        self.fsuuid = fsuuid
        self.mount_point = mount_point
        self.model = model
        self.vendror = vendror
        self.used = used
        self.serial_no = serial_no
        self.rmversion = rmversion
        self.fstype = fstype
        self.ssd = ssd
        self.size = size
        self.device_number = device_number
        self.driver = driver
        self.drive_status = drive_status
        self.group = group
        self.device = device
        self.bios_id = bios_id
        self.state = state
        self.driver_status = driver_status
        self.label = label
        self.req_queue_size = req_queue_size
        self.driver_mosules = driver_mosules
        self.mode = mode
        self.owner = owner
        self.min_io_size = min_io_size
        self.major_to_minor_no = major_to_minor_no
        self.device_files = device_files
        self.sysfs_busid = sysfs_busid
        self.alignment = alignment
        self.read_only = read_only
        self.read_ahead = read_ahead
        self.removable_device = removable_device
        self.scheduler_name = scheduler_name
        self.sysfs_id = sysfs_id
        self.sysfs_device_link = sysfs_device_link
        self.geo_bios_edd = geo_bios_edd
        self.geo_bios_legacy = geo_bios_legacy
        self.geo_logical = geo_logical
        self.phy_sector_size = phy_sector_size
        self.discard_granularity = discard_granularity
        self.discard_align_offset = discard_align_offset
        self.discard_max_bytes = discard_max_bytes
        self.discard_zeros_data = discard_zeros_data
        self.optimal_io_size = optimal_io_size
        self.log_sector_size = log_sector_size
        self._etcd_cls = _DiskEtcd

class _DiskEtcd(EtcdObj):
    """A table of the service, lazily updated

    """
    __name__ = 'nodes/%s/Disks/%s'
    _tendrl_cls = Disk

    def render(self):
        self.__name__ = self.__name__ % (
            tendrl_ns.node_context.node_id, self.disk_id
        )
        return super(_DiskEtcd, self).render()
