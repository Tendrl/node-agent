import json
import time


class Disk(object):
    """A table of the Disk, lazily updated

    """
    __name__ = 'nodes/%s/Disks/%s'

    def __init__(self, disk):
        self.updated = str(time.time()),
        self.disk_id = disk["disk_id"],
        self.node_id = disk['node_id'],
        self.device_name = disk["device_name"],
        self.disk_kernel_name = disk["disk_kernel_name"],
        self.parent_id = disk["parent_id"],
        self.parent_name = disk["parent_name"],
        self.disk_type = disk["disk_type"],
        self.fsuuid = disk["fsuuid"],
        self.mount_point = disk["mount_point"],
        self.model = disk["model"],
        self.vendor = disk["vendor"],
        self.used = disk["used"],
        self.serial_no = disk["serial_no"],
        self.rmversion = disk["rmversion"],
        self.fstype = disk["fstype"],
        self.ssd = disk["ssd"],
        self.size = disk["size"],
        self.drive_status = disk["drive_status"],
        self.device_number = disk["device_number"],
        self.driver = disk["driver"],
        self.group = disk["group"],
        self.device = disk["group"],
        self.state = disk["state"],
        self.label = disk["label"],
        self.req_queue_size = disk["req_queue_size"],
        self.driver_modules = disk["driver_modules"],
        self.mode = disk["mode"],
        self.owner = disk["owner"],
        self.bios_id = disk["bios_id"],
        self.min_io_size = disk["min_io_size"],
        self.major_to_minor_no = disk["major_to_minor_no"],
        self.device_files = disk["device_files"],
        self.sysfs_busid = disk["sysfs_busid"],
        self.alignement = disk["alignement"],
        self.read_only = disk["read_only"],
        self.read_ahead = disk["read_ahead"],
        self.removable_device = disk["removable_device"],
        self.scheduler_name = disk["scheduler_name"],
        self.sysfs_id = disk["sysfs_id"],
        self.sysfs_device_link = disk["sysfs_device_link"],
        self.geo_bios_edd = disk['geo_bios_edd'],
        self.geo_bios_legacy = disk["geo_bios_legacy"],
        self.geo_logical = disk["geo_logical"],
        self.phy_sector_size = disk["phy_sector_size"],
        self.discard_granularity = disk["discard_granularity"],
        self.discard_align_offset = disk["discard_align_offset"],
        self.discard_max_bytes = disk["discard_max_bytes"],
        self.discard_zeroes_data = disk["discard_zeroes_data"],
        self.optimal_io_size = disk["optimal_io_size"],
        self.log_sector_size = disk["log_sector_size"]

    def to_json_string(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def to_obj(json_str):
        return Disk(json.loads(json_str))
