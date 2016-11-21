from tendrl.node_agent.persistence.disk import Disk


class TestDisk(object):
    def test_disk(self):
        disk = {'phy_sector_size': '512',
                'label': '',
                'node_id': 'dddsad-121d-sad-sad',
                'discard_max_bytes': '2147450880',
                'mount_point': '',
                'discard_granularity': '512',
                'discard_align_offset': '0',
                'model': '',
                'used': '',
                'serial_no': '',
                'drive_status': '',
                'geo_bios_edd': '',
                'geo_logical': '',
                'alignement': '0',
                'disk_id': u'sdsaddsaSDSAFDSa',
                'req_queue_size': '128',
                'geo_bios_legacy': u'CHS 1023/255/63',
                'parent_name': '',
                'removable_device': False,
                'driver': [u'"ahci"', u'"sd"'],
                'disk_type': u'disk',
                'Model': u'"SAMSUNG MZ7TE512"',
                'fstype': '',
                'parent_id': '',
                'rmversion': u'"6L0Q"',
                'mode': 'brw-rw----',
                'disk_kernel_name': '/dev/sdb',
                'major_to_minor_no': '8:0',
                'scheduler_name': 'cfq',
                'state': 'running',
                'fsuuid': '',
                'sysfs_busid': u'0',
                'log_sector_size': '512',
                'sysfs_device_link': u'/devices/pci0000',
                'read_only': False,
                'bios_id': u'0x80',
                'driver_modules': [u'"ahci"'],
                'size': '512110190592',
                'device': u'"MZ7TE512"',
                'read_ahead': '128',
                'ssd': True,
                'owner': 'root',
                'min_io_size': '512',
                'sysfs_id': u'/class/block/sdb',
                'vendor': u'"SAMSUNG"',
                'group': 'disk',
                'device_files': [
                    u'/dev/sdb',
                    u'/dev/disk/by-id/ata-SAMSUNG'
                    '_MZ7TE512HMHP-000L1_S1GJNSAG400778',
                    u'/dev/disk/by-id/wwn-0x4d30445853885002'
                ],
                'device_number': u'block 8',
                'device_name': u'/dev/sdb',
                'optimal_io_size': '0',
                'discard_zeroes_data': '0'
                }
        self.disk = Disk(disk)
        result = self.disk.to_json_string()
        result_obj = self.disk.to_obj(result)
        assert isinstance(result_obj, Disk)
