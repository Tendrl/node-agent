import platform
import socket
import sys

from mock import MagicMock

from tendrl.node_agent.manager import pull_service_status

sys.modules['tendrl.node_agent.ansible_runner.ansible_module_runner'] = \
    MagicMock()

from tendrl.commons.utils import cmd_utils
import tendrl.node_agent.manager.pull_hardware_inventory as hi
from tendrl.node_agent.manager import utils as mgr_utils
del sys.modules['tendrl.node_agent.ansible_runner.ansible_module_runner']


class Test_pull_hardware_inventory(object):
    def test_getNodeCpu(self, monkeypatch):

        def mock_cmd_run(obj, exec_path):
            out = {
                u'changed': True,
                u'end': u'2016-11-07 16:56:37.674368',
                u'stdout': u'Architecture:          '
                'x86_64\nCPU op-mode(s):        32-bit, 64-bit\nByte Order:'
                '            Little Endian\nCPU(s):                '
                '4\nOn-line CPU(s) list:   0-3\nThread(s) per core:    '
                '2\nCore(s) per socket:    2\nSocket(s):             '
                '1\nNUMA node(s):          1\nVendor ID:             '
                'GenuineIntel\nCPU family:            6\nModel:               '
                '  78\nModel name:            Intel(R) Core(TM) i7-6600U CPU '
                '@ 2.60GHz\nStepping:              3\nCPU MHz:               '
                '2819.031\nCPU max MHz:           3400.0000\nCPU min MHz:     '
                '      400.0000\nBogoMIPS:              '
                '5616.51\nVirtualization:        VT-x\nL1d cache:             '
                '32K\nL1i cache:             32K\nL2 cache:              '
                '256K\nL3 cache:              4096K\nNUMA node0 CPU(s):     '
                '0-3\nFlags:                 fpu vme de pse tsc msr pae mce '
                'cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi '
                'mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm '
                'constant_tsc art arch_perfmon pebs bts rep_good nopl '
                'xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq '
                'dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 '
                'xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt '
                'tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm '
                '3dnowprefetch epb intel_pt tpr_shadow vnmi flexpriority ept'
                ' vpid fsgsbase tsc_adjust bmi1 hle avx2 smep bmi2 erms '
                'invpcid rtm mpx rdseed adx smap clflushopt xsaveopt xsavec '
                'xgetbv1 dtherm ida arat pln pts hwp hwp_notify '
                'hwp_act_window hwp_epp',
                u'cmd': [u'lscpu'],
                u'start': u'2016-11-07 16:56:37.671045',
                u'delta': u'0:00:00.003323',
                u'stderr': u'',
                u'rc': 0,
                u'invocation': {
                    u'module_args': {
                        u'creates': None,
                        u'executable': None,
                        u'chdir': None,
                        u'_raw_params': u'lscpu',
                        u'removes': None,
                        u'warn': True,
                        u'_uses_shell': False}
                }, u'warnings': []
            }

            return out, "", 0
        monkeypatch.setattr(cmd_utils.Command, 'run', mock_cmd_run)

        cpu = hi.getNodeCpu()
        cpu_expected = {
            "Model": "78", "VendorId": "GenuineIntel",
            "ModelName": "Intel(R) Core(TM) i7-6600U CPU @ 2.60GHz",
            "Architecture": "x86_64", "CoresPerSocket": "2",
            "CpuOpMode": "32-bit, 64-bit", "CPUFamily": "6", "CPUs": "4"
        }
        assert cpu == cpu_expected

        def mock_cmd_run(obj, exec_path):
            out = {
                u'changed': True,
                u'end': u'2016-11-07 16:56:37.674368',
                u'stdout': u'',
                u'cmd': [u'lscpu'],
                u'start': u'2016-11-07 16:56:37.671045',
                u'delta': u'0:00:00.003323',
                u'stderr': u'',
                u'rc': 0,
                u'invocation': {
                    u'module_args': {
                        u'creates': None,
                        u'executable': None,
                        u'chdir': None,
                        u'_raw_params': u'lscpu',
                        u'removes': None,
                        u'warn': True,
                        u'_uses_shell': False}
                }, u'warnings': []
            }
            return out, "", 0
        monkeypatch.setattr(cmd_utils.Command, 'run', mock_cmd_run)

        cpu = hi.getNodeCpu()
        cpu_expected = {
            "Model": "", "VendorId": "",
            "ModelName": "",
            "Architecture": "", "CoresPerSocket": "",
            "CpuOpMode": "", "CPUFamily": "", "CPUs": ""
        }
        assert cpu == cpu_expected

    def test_getNodeMemory(self, monkeypatch):

        def mock_cmd_run(obj, exec_path):
            out = {
                u'changed': True, u'end': u'2016-11-07 17:17:39.647578',
                u'stdout': u'MemTotal:       19965224 kB\nMemFree:    '
                '    12741812 kB\nMemAvailable:   14946552 kB\nBuffers:'
                '          312604 kB\nCached:          2810340 kB\nSwapCached:'
                '            0 kB\nActive:          5096660 kB\nInactive:     '
                '   1631012 kB\nActive(anon):    3608124 kB\nInactive(anon):'
                '   758808 kB\nActive(file):    1488536 kB\nInactive(file): '
                '  872204 kB\nUnevictable:          16 kB\nMlocked:         '
                '     16 kB\nSwapTotal:      10487804 kB\nSwapFree:       '
                '10487804 kB\nDirty:               864 kB\nWriteback:      '
                '       0 kB\nAnonPages:       3604320 kB\nMapped:         '
                '  715212 kB\nShmem:            762216 kB\nSlab:           '
                '  281052 kB\nSReclaimable:     208724 kB\nSUnreclaim:     '
                '   72328 kB\nKernelStack:       12224 kB\nPageTables:     '
                '   65184 kB\nNFS_Unstable:          0 kB\nBounce:         '
                '       0 kB\nWritebackTmp:          0 kB\nCommitLimit:    '
                '20470416 kB\nCommitted_AS:   10708208 kB\nVmallocTotal:   '
                '34359738367 kB\nVmallocUsed:           0 kB\nVmallocChunk:'
                '          0 kB\nHardwareCorrupted:     0 kB\nAnonHugePages:'
                '         0 kB\nCmaTotal:              0 kB\nCmaFree:       '
                '        0 kB\nHugePages_Total:       0\nHugePages_Free:    '
                '    0\nHugePages_Rsvd:        0\nHugePages_Surp:        '
                '0\nHugepagesize:       2048 kB\nDirectMap4k:      233072 kB'
                '\nDirectMap2M:     7553024 kB\nDirectMap1G:    12582912 kB',
                u'cmd': [u'cat', u'/proc/meminfo'],
                u'start': u'2016-11-07 17:17:39.645938',
                u'delta': u'0:00:00.001640',
                u'stderr': u'', u'rc': 0,
                u'invocation': {
                    u'module_args': {
                        u'creates': None,
                        u'executable': None,
                        u'chdir': None,
                        u'_raw_params': u'cat /proc/meminfo',
                        u'removes': None, u'warn': True,
                        u'_uses_shell': False
                    }
                },
                u'warnings': []
            }

            return out, "", 0
        monkeypatch.setattr(cmd_utils.Command, 'run', mock_cmd_run)

        memory = hi.getNodeMemory()
        memory_expected = {"TotalSize": "19965224 kB",
                           "SwapTotal": "10487804 kB"}
        assert memory == memory_expected

        def mock_cmd_run(obj, exec_path):
            out = {
                u'changed': True, u'end': u'2016-11-07 17:17:39.647578',
                u'stdout': u'',
                u'cmd': [u'cat', u'/proc/meminfo'],
                u'start': u'2016-11-07 17:17:39.645938',
                u'delta': u'0:00:00.001640',
                u'stderr': u'', u'rc': 0,
                u'invocation': {
                    u'module_args': {
                        u'creates': None,
                        u'executable': None,
                        u'chdir': None,
                        u'_raw_params': u'cat /proc/meminfo',
                        u'removes': None, u'warn': True,
                        u'_uses_shell': False
                    }
                },
                u'warnings': []
            }

            return out, "", 0
        monkeypatch.setattr(cmd_utils.Command, 'run', mock_cmd_run)

        memory = hi.getNodeMemory()
        memory_expected = {"TotalSize": "",
                           "SwapTotal": ""}
        assert memory == memory_expected

    def test_getNodeOs(self, monkeypatch):

        def mock_cmd_run(obj, exec_path):
            out = {
                u'changed': True, u'end': u'2016-11-07 17:27:45.909621',
                u'stdout': u'Enforcing',
                u'cmd': [u'getenforce'],
                u'start': u'2016-11-07 17:27:45.906818',
                u'delta': u'0:00:00.002803', u'stderr': u'',
                u'rc': 0, u'invocation': {
                    u'module_args': {
                        u'creates': None, u'executable': None,
                        u'chdir': None, u'_raw_params': u'getenforce',
                        u'removes': None, u'warn': True,
                        u'_uses_shell': False}}, u'warnings': []
            }

            return out, "", 0
        monkeypatch.setattr(cmd_utils.Command, 'run', mock_cmd_run)

        def mock_linux_distribution():
            return ["Fedora", "24"]
        monkeypatch.setattr(platform, 'linux_distribution',
                            mock_linux_distribution)

        def mock_release():
            return "4.6.4-301.fc24.x86_64"
        monkeypatch.setattr(platform, 'release',
                            mock_release)

        def mock_node():
            return "asdf.example.com"
        monkeypatch.setattr(socket, 'getfqdn',
                            mock_node)

        os = hi.getNodeOs()
        os_expected = {
            "KernelVersion": "4.6.4-301.fc24.x86_64",
            "SELinuxMode": "Enforcing",
            "OSVersion": "24",
            "Name": "Fedora",
            "FQDN": "asdf.example.com"
        }

        assert os == os_expected

    def test_get_node_inventory(self, monkeypatch):

        def mock_cmd_run(obj, exec_path):
            out = {
                u'changed': True, u'end': u'2016-11-07 17:40:56.549754',
                u'stdout': u'5bb3458a09004b2d9bdadf0705889958',
                u'cmd': [
                    u'cat', u'/etc/machine-id'],
                u'start': u'2016-11-07 17:40:56.547528',
                u'delta': u'0:00:00.002226', u'stderr': u'',
                u'rc': 0,
                u'invocation': {
                    u'module_args': {
                        u'creates': None,
                        u'executable': None,
                        u'chdir': None,
                        u'_raw_params': u'cat /etc/machine-id',
                        u'removes': None,
                        u'warn': True,
                        u'_uses_shell': False
                    }
                },
                u'warnings': []
            }
            return out, "", 0

        monkeypatch.setattr(cmd_utils.Command, 'run', mock_cmd_run)

        def mock_get_local_node_context():
            return "e3bf35c1-31e6-421a-bd68-f22ce2274d96"
        monkeypatch.setattr(
            mgr_utils, 'get_local_node_context', mock_get_local_node_context)

        def mock_getNodeOs():
            return {
                "KernelVersion": "4.6.4-301.fc24.x86_64",
                "SELinuxMode": "Enforcing",
                "OSVersion": "24", "Name": "Fedora",
                "FQDN": "asdf.example.com"
            }
        monkeypatch.setattr(hi, 'getNodeOs',
                            mock_getNodeOs)

        def mock_getNodeMemory():
            return {
                "TotalSize": "19965224 kB",
                "SwapTotal": "10487804 kB"
            }
        monkeypatch.setattr(hi, 'getNodeMemory',
                            mock_getNodeMemory)

        def mock_getTendrlContext():
            return {
                "sds_name": "gluster",
                "sds_version": "3.4.5"
            }
        monkeypatch.setattr(hi, 'getTendrlContext',
                            mock_getTendrlContext)

        def mock_getNodeCpu():
            return {
                "Model": "78", "VendorId": "GenuineIntel",
                "ModelName": "Intel(R) Core(TM) i7-6600U CPU @ 2.60GHz",
                "Architecture": "x86_64", "CoresPerSocket": "2",
                "CpuOpMode": "32-bit, 64-bit", "CPUFamily": "6", "CPUs": "4"
            }
        monkeypatch.setattr(hi, 'getNodeCpu',
                            mock_getNodeCpu)

        def mock_get_node_disks():
            return{
                "model": "",
                "disk_id": "",
                "vendor": "0x1af4",
                "name": "/dev/vdc",
                "ssd": False,
                "fs_type": "",
                "mount_point": [""],
                "parent": "",
                "fs_uuid": "",
                "used": False,
                "type": "disk",
                "device_name": "/dev/vdc",
                "size": 536870912000L
            }
        monkeypatch.setattr(hi, 'get_node_disks',
                            mock_get_node_disks)
        pull_service_status.node_service_details = MagicMock()
        node_inventory = hi.get_node_inventory()
        node_inventory_expected = {
            "machine_id": "5bb3458a09004b2d9bdadf0705889958",
            "node_id": 'e3bf35c1-31e6-421a-bd68-f22ce2274d96',
            "os": {
                "KernelVersion": "4.6.4-301.fc24.x86_64",
                "SELinuxMode": "Enforcing", "OSVersion": "24",
                "Name": "Fedora", "FQDN": "asdf.example.com"
            },
            "cpu": {
                "Model": "78",
                "VendorId": "GenuineIntel",
                "ModelName": "Intel(R) Core(TM) i7-6600U CPU @ 2.60GHz",
                "Architecture": "x86_64", "CoresPerSocket": "2",
                "CpuOpMode": "32-bit, 64-bit", "CPUFamily": "6",
                "CPUs": "4"
            },
            "memory": {
                "TotalSize": "19965224 kB", "SwapTotal": "10487804 kB"
            },
            "tendrl_context": {
                "sds_name": "gluster",
                "sds_version": "3.4.5"
            },
            "disks": {
                "model": "",
                "disk_id": "",
                "vendor": "0x1af4",
                "name": "/dev/vdc",
                "ssd": False,
                "fs_type": "",
                "mount_point": [""],
                "parent": "",
                "fs_uuid": "",
                "used": False,
                "type": "disk",
                "device_name": "/dev/vdc",
                "size": 536870912000
            },
            "services": pull_service_status.node_service_details
        }
        assert node_inventory == node_inventory_expected

    def test_get_node_disks(self, monkeypatch):
        self.cmd_obj = ""
        out1 = {
            u'stdout': u'[Created at block.434]\n'
            'Unique ID: bdUI.SE1wIdpsiiC\n'
            'Parent ID: 3OOL.qPX1W_dGFo7\n'
            'SysFS ID: /class/block/sda/sda1\n'
            'Hardware Class: partition\n'
            'Model: "Partition"\n'
            'Device File: /dev/sda1\n'
            'Device Files: /dev/sda1, '
            '/dev/disk/by-id/ata-SAMSUNG_'
            'MZ7TE512HMHP-000L1_S1GJNSAG400778-part1, '
            '/dev/disk/by-id/wwn-0x4d30445853885002-part1, '
            '/dev/disk/by-uuid/dda9f15f-c5ec-4674-894a-d9ae57b8243c\n'
            'Config Status: cfg=new, avail=yes, need=no, active=unknown\n'
            'Attached to: #18 (Disk)\n\n'
            '[Created at block.245]\n'
            'Unique ID: 3OOL.qPX1W_dGFo7\n'
            'Parent ID: w7Y8.HhbUszJC6y1\n'
            'SysFS ID: /class/block/sda\n'
            'SysFS BusID: 0:0:0:0\n'
            'SysFS Device Link: /devices/pci0000:00/0000:00:1f.2'
            '/ata1/host0/target0:0:0/0:0:0:0\n'
            'Hardware Class: disk\n'
            'Model: "SAMSUNG MZ7TE512"\n'
            'Device: "MZ7TE512"\n'
            'Revision: "6L0Q"\n'
            'Driver: "ahci", "sd"\n'
            'Driver Modules: "ahci"\n'
            'Device File: /dev/sda\n'
            'Device Files: /dev/sda, /dev/disk/by-id/ata-'
            'SAMSUNG_MZ7TE512HMHP-000L1_S1GJNSAG400778, '
            '/dev/disk/by-id/wwn-0x4d30445853885002\n'
            'Device Number: block 8:0-8:15\n'
            'BIOS id: 0x80\n'
            'Geometry (BIOS EDD): CHS 992277/16/63\n'
            'Size (BIOS EDD): 1000215216 sectors\n'
            'Geometry (BIOS Legacy): CHS 1023/255/63\n\n'
            '[Created at block.245]\n'
            'Unique ID: sdsaddsaSDSAFDSa\n'
            'Parent ID: sdsafkdsaSDvfv\n'
            'SysFS ID: /class/block/sdb\n'
            'SysFS BusID: 0:0:0:0\n'
            'SysFS Device Link: /devices/pci0000:00/0000:00:1f.2'
            '/ata1/host0/target0:0:0/0:0:0:0\n'
            'Hardware Class: disk\n'
            'Model: "SAMSUNG MZ7TE512"\n'
            'Vendor: "SAMSUNG"\n'
            'Serial ID: "S1GJNSAG400778"\n'
            'Device: "MZ7TE512"\n'
            'Revision: "6L0Q"\n'
            'Driver: "ahci", "sd"\n'
            'Driver Modules: "ahci"\n'
            'Device File: /dev/sdb\n'
            'Device Files: /dev/sdb, /dev/disk/by-id/ata-'
            'SAMSUNG_MZ7TE512HMHP-000L1_S1GJNSAG400778, '
            '/dev/disk/by-id/wwn-0x4d30445853885002\n'
            'Device Number: block 8:0-8:15\n'
            'BIOS id: 0x80\n'
            'Geometry (BIOS EDD): CHS 992277/16/63\n'
            'Size (BIOS EDD): 1000215216 sectors\n'
            'Geometry (BIOS Legacy): CHS 1023/255/63\n',
            u'stderr': u''
        }
        out2 = {
            u'stdout': '/dev/sda /dev/sda  8:0     '
            '128 0 0 512110190592 running root disk brw-rw---- '
            '0 512 0 512 512 0 cfq 128 0 512 2147450880 0\n'
            '/dev/sda1 /dev/sda1 /dev/sda 8:1 ext4 /boot  '
            'dda9f15f-c5ec-4674-894a-d9ae57b8243c 128 0 0 1073741824  '
            'root disk brw-rw---- 0 512 0 512 512 0 cfq 128 0 '
            '512 2147450880 0 SAMSOUNG XAM004\n'
            '/dev/sdb /dev/sdb  8:0     '
            '128 0 0 512110190592 running root disk brw-rw---- '
            '0 512 0 512 512 0 cfq 128 0 512 2147450880 0\n',
            u'stderr': ''
        }
        self.count = 0

        def mock_cmd_run(value, exec_path):
            if self.count <= 2:
                self.count += 1
                return out1, "", 0
            else:
                return out2, "", 0

        monkeypatch.setattr(cmd_utils.Command, 'run', mock_cmd_run)
        expected = (
            {
                'used_disks_id': [u'bdUI.SE1wIdpsiiC'],
                'free_disks_id': [u'sdsaddsaSDSAFDSa'],
                'disks': [
                    {'phy_sector_size': '512',
                     'label': '',
                     'discard_max_bytes': '2147450880',
                     'mount_point': '',
                     'discard_granularity': '512',
                     'discard_align_offset': '0',
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
                     },
                    {'phy_sector_size': '512',
                     'label': '',
                     'mount_point': '/boot',
                     'alignement': '0',
                     'req_queue_size': '128',
                     'parent_name': '/dev/sda',
                     'disk_type': u'partition',
                     'Model': u'"Partition"',
                     'sysfs_busid': '',
                     'mode': 'brw-rw----',
                     'min_io_size': '512',
                     'read_ahead': '128',
                     'disk_id': u'bdUI.SE1wIdpsiiC',
                     'vendor': 'SAMSOUNG',
                     'device_number': '',
                     'discard_granularity': '512',
                     'discard_align_offset': '0',
                     'geo_bios_legacy': '',
                     'removable_device': False,
                     'driver': '',
                     'fstype': 'ext4',
                     'parent_id': u'3OOL.qPX1W_dGFo7',
                     'rmversion': '',
                     'ssd': False,
                     'disk_kernel_name': '/dev/sda1',
                     'major_to_minor_no': '8:1',
                     'scheduler_name': 'cfq',
                     'device_files': [
                         u'/dev/sda1',
                         u'/dev/disk/by-id/ata-SAMSUNG_'
                         'MZ7TE512HMHP-000L1_S1GJNSAG400778-part1',
                         u'/dev/disk/by-id/'
                         'wwn-0x4d30445853885002-part1',
                         u'/dev/disk/by-uuid/'
                         'dda9f15f-c5ec-4674-894a-d9ae57b8243c'
                     ],
                     'fsuuid': 'dda9f15f-c5ec-4674-894a-d9ae57b8243c',
                     'read_only': False,
                     'log_sector_size': '512',
                     'sysfs_device_link': '',
                     'group': 'disk',
                     'bios_id': '',
                     'size': '1073741824',
                     'device': '',
                     'discard_max_bytes': '2147450880',
                     'owner': 'root',
                     'driver_modules': '',
                     'sysfs_id': u'/class/block/sda/sda1',
                     'state': '',
                     'device_name': u'/dev/sda1',
                     'optimal_io_size': '0',
                     'discard_zeroes_data': '0'
                     }]})
        result = hi.get_node_disks()
        for exp in expected:
            assert exp in result

    def test_get_node_disks_error(self, monkeypatch):
        out = {"stderr": "Error"}

        def mock_cmd_run(value, exec_path):
            return out, "", 0
        monkeypatch.setattr(cmd_utils.Command, 'run', mock_cmd_run)
        result = hi.get_node_disks()
        assert result == {"free_disks_id": [],
                          "used_disks_id": [],
                          "disks": []}
