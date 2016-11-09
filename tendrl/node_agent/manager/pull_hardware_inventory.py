from command import Command
import platform

node_agent_key = ""


def getNodeCpu():
    '''returns structure

    {"nodename": [{"Architecture":   "architecture",

                   "CpuOpMode":      "cpuopmode",

                   "CPUs":           "cpus",

                   "VendorId":       "vendorid",

                   "ModelName":      "modelname",

                   "CPUFamily":      "cpufamily",

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
            'Model': info_list[11].split(':')[1].strip(),
            'CoresPerSocket': info_list[6].split(':')[1].strip()
        }
    else:
            cpuinfo = {
                'Architecture': '', 'CpuOpMode': '',
                'CPUs': '', 'VendorId': '',
                'ModelName': '', 'CPUFamily': '',
                'Model': '', 'CoresPerSocket': ''
            }

    return cpuinfo


def getNodeMemory():
    '''returns structure

    {"nodename": [{"TotalSize": "totalsize",

                   "SwapTotal": "swaptotal",

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
            'SwapTotal': info_list[14].split(':')[1].strip()
        }
    else:
        memoinfo = {
            'TotalSize': '',
            'SwapTotal': ''
        }

    return memoinfo


def getNodeOs():
    cmd = Command({"_raw_params": "getenforce"})
    out, err = cmd.start()
    se_out = out['stdout']

    osinfo = {}
    os_out = platform.linux_distribution()

    osinfo = {
        'Name': os_out[0],
        'OSVersion': os_out[1],
        'KernelVersion': platform.release(),
        'SELinuxMode': se_out,
        'FQDN': platform.node()
    }

    return osinfo


def update_node_agent_key(file_name):
    global node_agent_key
    node_agent_key = file_name


def get_node_inventory():
    node_inventory = {}

    cmd = Command({"_raw_params": "cat /etc/machine-id"})
    out, err = cmd.start()
    out = out['stdout']

    node_inventory["node_machine_uuid"] = out
    cmd = Command({"_raw_params": "cat %s" % node_agent_key})
    out, err = cmd.start()
    out = out['stdout']

    node_inventory["node_uuid"] = out

    node_inventory["os"] = getNodeOs()
    node_inventory["cpu"] = getNodeCpu()
    node_inventory["memory"] = getNodeMemory()

    return node_inventory
