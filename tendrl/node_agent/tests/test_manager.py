import gevent.event
from mock import MagicMock
import sys
sys.modules['tendrl.commons.config'] = MagicMock()
sys.modules['tendrl.commons.log'] = MagicMock()
sys.modules['tendrl.node_agent.persistence.persister'] = MagicMock()
from tendrl.commons.manager.manager import SyncStateThread
from tendrl.commons.manager.rpc_job_process import RpcJobProcessThread
from tendrl.node_agent.manager import manager
del sys.modules['tendrl.commons.log']
del sys.modules['tendrl.commons.config']
del sys.modules['tendrl.node_agent.persistence.persister']


class TestNodeAgentManager(object):
    def setup_method(self, method):
        manager.pull_hardware_inventory = MagicMock()
        manager.utils = MagicMock()
        manager.NodeAgentManager.load_and_execute_platform_discovery_plugins\
            = MagicMock()
        manager.NodeAgentManager.load_and_execute_sds_discovery_plugins = \
            MagicMock()
        self.manager = manager.NodeAgentManager(
            'aa22a6fe-87f0-45cf-8b70-2d0ff4c02af6'
        )

    def test_manager_constructor(self):
        assert isinstance(
            self.manager._rpc_job_process_thread,
            RpcJobProcessThread
        )
        assert isinstance(
            self.manager._complete,
            gevent.event.Event
        )
        assert isinstance(
            self.manager._discovery_thread,
            SyncStateThread
        )
        assert self.manager.defs_dir == "/tendrl_definitions_node_agent/data"

    def test_register_node(self):
        self.manager.persister_thread.update_node_context.assert_called()
        self.manager.persister_thread.update_node_context.assert_called()
        self.manager.persister_thread.update_tendrl_definitions.assert_called()


class TestNodeAgentSyncStateThread(object):
    def setup_method(self, method):
        manager.gevent = MagicMock()
        manager.json = MagicMock()
        self.manager = manager.NodeAgentManager(
            'aa22a6fe-87f0-45cf-8b70-2d0ff4c02af6'
        )
        self.SyncStateThread = manager.NodeAgentSyncStateThread(self.manager)
        self.ret = True

    def test_run(self, monkeypatch):
        node_inventory = (
            {
                "node_id": "0e4f5489-4cc3-4264-84be-b4fc9a6259e7",
                "memory": {"TotalSize": "1016188 kB",
                           "SwapTotal": "0 kB"
                           },
                "machine_id": "0a9f65533cdf4cf2abc4b8ba7f7b2aba",
                "os": {"KernelVersion": "3.10.0-123.el7.x86_64",
                       "SELinuxMode": "Enforcing",
                       "OSVersion": "7.0.1406",
                       "Name": "CentOS Linux",
                       "FQDN": "dhcp41-152.lab.eng.blr.redhat.com"
                       },
                "cpu": {"Model": "42",
                        "VendorId": "GenuineIntel",
                        "ModelName": "Intel Xeon E312xx (Sandy Bridge)",
                        "Architecture": "x86_64",
                        "CoresPerSocket": "1",
                        "CpuOpMode": "32-bit, 64-bit",
                        "CPUFamily": "6",
                        "CPUs": "1"
                        },
                "tendrl_context": {"sds_version": "10.2.3",
                                   "sds_name": "ceph"
                                   },
                "disks": {"disks": [{'phy_sector_size': '512',
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
                                         '_MZ7TE512HMHP-000L1_'
                                         'S1GJNSAG400778',
                                         u'/dev/disk/by-id/wwn'
                                         '-0x4d30445853885002'
                                     ],
                                     'device_number': u'block 8',
                                     'device_name': u'/dev/sdb',
                                     'optimal_io_size': '0',
                                     'discard_zeroes_data': '0'
                                     }],
                          "free_disks_id": ["sdssds"],
                          "used_disks_id": ["sadAS"]}
            })
        self.manager.etcd_orm.client.delete = MagicMock()
        self.manager.etcd_orm.client.write = MagicMock()
        self.disk = False

        def mock_to_json_string(param):
            self.disk = True
        monkeypatch.setattr(
            manager.Disk, "to_json_string", mock_to_json_string)
        manager.pull_hardware_inventory.get_node_inventory = \
            MagicMock(return_value=node_inventory)
        self.SyncStateThread._complete = self
        self.SyncStateThread._run()
        self.manager.persister_thread.update_node_context.assert_called()
        self.manager.persister_thread.update_node.assert_called()
        self.manager.persister_thread.update_tendrl_context.assert_called()
        self.manager.persister_thread.update_os.assert_called()
        self.manager.persister_thread.update_memory.assert_called()
        self.manager.persister_thread.update_cpu.assert_called()
        assert self.disk

    def is_set(self):
        self.ret = not self.ret
        return self.ret
