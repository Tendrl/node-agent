import platform
from tendrl.node_agent.manager.command import Command
import tendrl.node_agent.manager.pull_hardware_inventory as hi


class Test_pull_hardware_inventory(object):
    def test_getNodeCpu(self, monkeypatch):

        def mock_cmd_start(obj):
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

            return out, ""
        monkeypatch.setattr(Command, 'start', mock_cmd_start)

        cpu = hi.getNodeCpu()
        cpu_expected = {
            "Model": "78", "VendorId": "GenuineIntel",
            "ModelName": "Intel(R) Core(TM) i7-6600U CPU @ 2.60GHz",
            "Architecture": "x86_64", "CoresPerSocket": "2",
            "CpuOpMode": "32-bit, 64-bit", "CPUFamily": "6", "CPUs": "4"
        }
        assert cpu == cpu_expected

        def mock_cmd_start(obj):
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
            return out, ""
        monkeypatch.setattr(Command, 'start', mock_cmd_start)

        cpu = hi.getNodeCpu()
        cpu_expected = {
            "Model": "", "VendorId": "",
            "ModelName": "",
            "Architecture": "", "CoresPerSocket": "",
            "CpuOpMode": "", "CPUFamily": "", "CPUs": ""
        }
        assert cpu == cpu_expected

    def test_getNodeMemory(self, monkeypatch):

        def mock_cmd_start(obj):
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

            return out, ""
        monkeypatch.setattr(Command, 'start', mock_cmd_start)

        memory = hi.getNodeMemory()
        memory_expected = {"TotalSize": "19965224 kB",
                           "SwapTotal": "10487804 kB"}
        assert memory == memory_expected

        def mock_cmd_start(obj):
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

            return out, ""
        monkeypatch.setattr(Command, 'start', mock_cmd_start)

        memory = hi.getNodeMemory()
        memory_expected = {"TotalSize": "",
                           "SwapTotal": ""}
        assert memory == memory_expected

    def test_getNodeOs(self, monkeypatch):

        def mock_cmd_start(obj):
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

            return out, ""
        monkeypatch.setattr(Command, 'start', mock_cmd_start)

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
        monkeypatch.setattr(platform, 'node',
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

        def mock_cmd_start(obj):
            if obj.attributes["_raw_params"] == "cat /etc/machine-id":
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
            else:
                out = {
                    u'changed': True, u'end': u'2016-11-07 17:40:56.549754',
                    u'stdout': u'e3bf35c1-31e6-421a-bd68-f22ce2274d96',
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

            return out, ""

        monkeypatch.setattr(Command, 'start', mock_cmd_start)

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

        def mock_getNodeCpu():
            return {
                "Model": "78", "VendorId": "GenuineIntel",
                "ModelName": "Intel(R) Core(TM) i7-6600U CPU @ 2.60GHz",
                "Architecture": "x86_64", "CoresPerSocket": "2",
                "CpuOpMode": "32-bit, 64-bit", "CPUFamily": "6", "CPUs": "4"
            }
        monkeypatch.setattr(hi, 'getNodeCpu',
                            mock_getNodeCpu)

        node_inventory = hi.get_node_inventory()
        node_inventory_expected = {
            "node_machine_uuid": "5bb3458a09004b2d9bdadf0705889958",
            "node_uuid": 'e3bf35c1-31e6-421a-bd68-f22ce2274d96',
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
            }
        }

        assert node_inventory == node_inventory_expected
