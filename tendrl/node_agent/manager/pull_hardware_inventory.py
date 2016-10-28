from command import Command
import json
import platform


def GetNodeCpu():
    '''returns structure

    {"nodename": [{"Architecture":   "architecture",

                   "CpuOpMode":      "cpuopmode",

                   "CPUs":           "cpus",

                   "VendorId":       "vendorid",

                   "ModelName":      "modelname",

                   "CPUFamily":      "cpufamily",

                   "CPUMHz":         "cpumhz",

                   "Model":          "Model",

                   "CoresPerSocket": "corespersocket"}, ...], ...}

    '''
    cmd = Command({"_raw_params": "lscpu"})
    out, err = cmd.start()
    out = out['stdout']
    cpuinfo = {}
    if out:
        info_list = out.split('\n')
        cpuinfo = {
            'Architecture': info_list[0].split(':')[1].strip(),
            'CpuOpMode': info_list[1].split(':')[1].strip(),
            'CPUs': info_list[3].split(':')[1].strip(),
            'VendorId': info_list[9].split(':')[1].strip(),
            'ModelName': info_list[12].split(':')[1].strip(),
            'CPUFamily': info_list[10].split(':')[1].strip(),
            'CPUMHz': info_list[14].split(':')[1].strip(),
            'Model': info_list[11].split(':')[1].strip(),
            'CoresPerSocket': info_list[6].split(':')[1].strip()
        }
    else:
            cpuinfo = {
                'Architecture': '', 'CpuOpMode': '',
                'CPUs': '', 'VendorId': '',
                'ModelName': '', 'CPUFamily': '',
                'CPUMHz': '', 'Model': '', 'CoresPerSocket': ''
            }

    return cpuinfo


def GetNodeMemory():
    '''returns structure

    {"nodename": [{"TotalSize": "totalsize",

                   "SwapTotal": "swaptotal",

                   "Active":    "active",

                   "Type":      "type"}, ...], ...}

    '''

    cmd = Command({"_raw_params": "cat /proc/meminfo"})
    out, err = cmd.start()
    out = out['stdout']

    memoinfo = {}
    if out:
        info_list = out.split('\n')
        memoinfo = {
            'TotalSize': info_list[0].split(':')[1].strip(),
            'SwapTotal': info_list[14].split(':')[1].strip(),
            'Active': info_list[6].split(':')[1].strip(),
            'Type': ''
        }
    else:
        memoinfo = {
            'TotalSize': '',
            'SwapTotal': '',
            'Active': '',
            'Type': ''
        }

    return memoinfo


def GetNodeOs():
    cmd = Command({"_raw_params": "getenforce"})
    out, err = cmd.start()
    se_out = out['stdout']

    osinfo = {}
    os_out = platform.linux_distribution()

    osinfo = {'Name': os_out[0],
              'OSVersion': os_out[1],
              'KernelVersion': platform.release(),
              'SELinuxMode': se_out}

    return osinfo


def write_node_inventory(file_path):
    node_inventory = {}

    cmd = Command({"_raw_params": "cat /etc/machine-id"})
    out, err = cmd.start()
    out = out['stdout']

    node_inventory["node_uuid"] = out

    node_inventory["os"] = GetNodeOs()
    node_inventory["cpu"] = GetNodeCpu()
    node_inventory["memory"] = GetNodeMemory()

    with open(file_path, 'w') as fp:
        json.dump(node_inventory, fp)

    return
