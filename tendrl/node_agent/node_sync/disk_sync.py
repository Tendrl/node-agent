from tendrl.commons.event import Event
from tendrl.commons.message import Message

from tendrl.commons.utils import cmd_utils
import os

def get_node_disks():
    disks, disks_map, err = get_disk_details()
    if not err:
        cmd = cmd_utils.Command('hwinfo --partition')
        out, err, rc = cmd.run()
        if not err:
           for partitions in out.split('\n\n'):
                devlist = {"hardware_id": "",
                           "parent_hardware_id": "",
                           "sysfs_id": "",
                           "hardware_class": "",
                           "model": "",
                           "partition_name": "",
                           "device_files": "",
                           "config_status": "",
                           }
                for partition in partitions.split('\n'):
                    key = partition.split(':')[0]
                    if key.strip() == "Unique ID":
                        devlist["hardware_id"] = \
                            partition.split(':')[1].lstrip()
                    if key.strip() == "Parent ID":
                        devlist["parent_hardware_id"] = \
                            partition.split(':')[1].lstrip()
                    if key.strip() == "SysFS ID":
                        devlist["sysfs_id"] = \
                            partition.split(':')[1].lstrip()
                    if key.strip() == "Hardware Class":
                        devlist["hardware_class"] = \
                            partition.split(':')[1].lstrip()
                    if key.strip() == "Model":
                        devlist["model"] = \
                            partition.split(':')[1].lstrip().replace('"', "")
                    if key.strip() == "Device File":
                        devlist["partition_name"] = \
                            partition.split(':')[1].lstrip()
                    if key.strip() == "Device Files":
                        devlist["device_files"] = \
                            partition.split(':')[1].lstrip()
                    if key.strip() == "Config Status":
                        devlist["config_status"] = \
                            partition.split(':')[1].lstrip()

                part_name = devlist["partition_name"]
                parent = disks_map[devlist["parent_hardware_id"]]
                disks[parent]["partitions"][part_name] = devlist
    return disks


def get_disk_details():
    disks = {}
    disks_map = {}
    cmd = cmd_utils.Command('hwinfo --disk')
    out, err, rc = cmd.run()
    if not err:
        out = out.encode('utf8')
        for all_disks in out.split('\n\n'):
            devlist = {"disk_id": "",
                       "hardware_id": "",
                       "disk_name": "",
                       "sysfs_id": "",
                       "sysfs_busid": "",
                       "sysfs_device_link": "",
                       "hardware_class": "", 
                       "model": "",
                       "vendor": "",
                       "device": "",
                       "rmversion": "",
                       "serial_no": "",
                       "driver_modules": "",
                       "driver": "",
                       "device_files": "",
                       "device_number": "",
                       "bios_id": "",
                       "geo_bios_edd": "",
                       "geo_logical": "",
                       "size": "",
                       "size_bios_edd": "",
                       "geo_bios_legacy": "",
                       "config_status": "",
                       "partitions": {}
                       }
            for disk in all_disks.split('\n'):
                key = disk.split(':')[0]
                if key.strip() == "Unique ID":
                    devlist["hardware_id"] = \
                        disk.split(':')[1].lstrip()
                elif key.strip() == "SysFS ID":
                    devlist["sysfs_id"] = \
                        disk.split(':')[1].lstrip()
                elif key.strip() == "SysFS BusID":
                    devlist["sysfs_busid"] = \
                        disk.split(':')[1].lstrip()
                elif key.strip() == "SysFS Device Link":
                    devlist["sysfs_device_link"] = \
                        disk.split(':')[1].lstrip()
                elif key.strip() == "Hardware Class":
                    devlist["hardware_class"] = \
                        disk.split(':')[1].lstrip()
                elif key.strip() == "Model":
                    devlist["model"] = \
                        disk.split(':')[1].lstrip().replace('"', "")
                elif key.strip() == "Vendor":
                    devlist["vendor"] = \
                        disk.split(':')[1].lstrip().replace('"', "")
                elif key.strip() == "Device":
                    devlist["device"] = \
                        disk.split(':')[1].lstrip().replace('"', "")
                elif key.strip() == "Revision":
                    devlist["rmversion"] = \
                        disk.split(':')[1].lstrip().replace('"', "")
                elif key.strip() == "Serial ID":
                    devlist["serial_no"] = \
                        disk.split(':')[1].lstrip().replace('"', "")
                elif key.strip() == "Driver":
                    devlist["driver"] = \
                        disk.split(':')[1].lstrip().replace('"', "")
                elif key.strip() == "Driver Modules":
                    devlist["driver_modules"] = \
                        disk.split(':')[1].lstrip().replace('"', "")
                elif key.strip() == "Device File":
                    devlist["disk_name"] = \
                        disk.split(':')[1].lstrip()
                elif key.strip() == "Device Files":
                    devlist["device_files"] = \
                        disk.split(':')[1].lstrip()
                elif key.strip() == "Device Number":
                    devlist["device_number"] = \
                        disk.split(':')[1].lstrip()
                elif key.strip() == "BIOS id":
                    devlist["bios_id"] = \
                        disk.split(':')[1].lstrip()
                elif key.strip() == "Geometry (Logical)":
                    devlist["geo_logical"] = \
                        disk.split(':')[1].lstrip()
                elif key.strip() == "Capacity":
                    devlist["size"] = \
                        disk.split('(')[1].split()[0]
                elif key.strip() == "Geometry (BIOS EDD)":
                    devlist["geo_bios_edd"] = \
                        disk.split(':')[1].lstrip()
                elif key.strip() == "Size (BIOS EDD)":
                    devlist["size_bios_edd"] = \
                        disk.split(':')[1].lstrip()
                elif key.strip() == "Geometry (BIOS Legacy)":
                    devlist["geo_bios_legacy"] = \
                        disk.split(':')[1].lstrip()
                elif key.strip() == "Config Status":
                    devlist["config_status"] = \
                        disk.split(':')[1].lstrip()
            if ("virtio" in devlist["driver"] and
                "by-id/virtio" in devlist['device_files']):
                # split from:
                # /dev/vdc, /dev/disk/by-id/virtio-0200f64e-5892-40ee-8,
                #    /dev/disk/by-path/virtio-pci-0000:00:08.0
                for entry in devlist['device_files'].split(','):
                    if "by-id/virtio" in entry:
                        devlist['disk_id'] = entry.split('/')[-1]
                        break
            elif (devlist["vendor"] != "" and
                devlist["device"] != "" and
                devlist["serial_no"] != ""):
                devlist["disk_id"] = (devlist["vendor"] + "_" +
                        devlist["device"] + "_" + devlist["serial_no"])
            else:
                devlist['disk_id'] = devlist['disk_name']

            disks[devlist["disk_id"]] = devlist
            disks_map[devlist['hardware_id']] = devlist["disk_id"]

    return disks, disks_map, err


def get_node_block_devices(disks_map):
    block_devices = {}
    block_devices['all'] = []
    block_devices['free'] = []
    block_devices['used'] = []
    columns = 'NAME,KNAME,PKNAME,MAJ:MIN,FSTYPE,MOUNTPOINT,LABEL,' \
              'UUID,RA,RO,RM,SIZE,STATE,OWNER,GROUP,MODE,ALIGNMENT,' \
              'MIN-IO,OPT-IO,PHY-SEC,LOG-SEC,ROTA,SCHED,RQ-SIZE,' \
              'DISC-ALN,DISC-GRAN,DISC-MAX,DISC-ZERO,TYPE'
    keys = columns.split(',')
    lsblk = (
        "lsblk --all --bytes --noheadings --output='%s' --path --raw" %
        columns)
    cmd = cmd_utils.Command(lsblk)
    out, err, rc = cmd.run()
    if not err:
        out = out.encode('utf8')
        devlist = map(
            lambda line: dict(zip(keys, line.split(' '))),
            out.splitlines())
        all_parents = []
        parent_ids = []
        for dev_info in devlist:
            device = {}
            device['device_name'] = dev_info['NAME']
            device['device_kernel_name'] = dev_info['KNAME']
            device['parent_name'] = dev_info['PKNAME']
            device['major_to_minor_no'] = dev_info['MAJ:MIN']
            device['fstype'] = dev_info['FSTYPE']
            device['mount_point'] = dev_info['MOUNTPOINT']
            device['label'] = dev_info['LABEL']
            device['fsuuid'] = dev_info['UUID']
            device['read_ahead'] = dev_info['RA']
            if dev_info['RO'] == '0':
                device['read_only'] = False
            else:
                device['read_only'] = True
            if dev_info['RM'] == '0':
                device['removable_device'] = False
            else:
                device['removable_device'] = True
            device['size'] = dev_info['SIZE']
            device['state'] = dev_info['STATE']
            device['owner'] = dev_info['OWNER']
            device['group'] = dev_info['GROUP']
            device['mode'] = dev_info['MODE']
            device['alignment'] = dev_info['ALIGNMENT']
            device['min_io_size'] = dev_info['MIN-IO']
            device['optimal_io_size'] = dev_info['OPT-IO']
            device['phy_sector_size'] = dev_info['PHY-SEC']
            device['log_sector_size'] = dev_info['LOG-SEC']
            device['device_type'] = dev_info['TYPE']
            device['scheduler_name'] = dev_info['SCHED']
            device['req_queue_size'] = dev_info['RQ-SIZE']
            device['discard_align_offset'] = dev_info['DISC-ALN']
            device['discard_granularity'] = dev_info['DISC-GRAN']
            device['discard_max_bytes'] = dev_info['DISC-MAX']
            device['discard_zeros_data'] = dev_info['DISC-ZERO']
            device['rotational'] = dev_info['ROTA']
            if dev_info['TYPE'] == 'disk':
                device['ssd'] = is_ssd(dev_info['ROTA'])
            else:
                device['ssd'] = False

            if dev_info['TYPE'] == 'part':
                device['used'] = True
                device['disk_id'] = disks_map[dev_info['PKNAME']]
                block_devices['all'].append(device)
                block_devices['used'].append(device['device_name'])

            if dev_info['TYPE'] == 'disk':
                device['disk_id'] = disks_map[dev_info['NAME']]
                all_parents.append(device)
            else:
                parent_ids.append(dev_info['PKNAME'])
        for parent in all_parents:
            if parent['device_name'] in parent_ids:
                parent['used'] = True
                block_devices['used'].append(parent['device_name'])
            else:
                parent['used'] = False
                block_devices['free'].append(parent['device_name'])
            block_devices['all'].append(parent)
    else:
        Event(
            Message(
                priority="error",
                publisher=NS.publisher_id,
                payload={"message": err}
            )
        )
    return block_devices


def get_raw_reference():
    base_path = '/dev/disk/'
    paths = os.listdir(base_path)
    raw_reference = {}
    for path in paths:
        raw_reference[path] = []
        full_path = base_path + path
        cmd = cmd_utils.Command("ls -l %s" % full_path)
        out, err, rc = cmd.run()
        if not err:
            out = out.encode('utf8')
            count = 0
            for line in out.split('\n'):
                if count == 0:
                    # to skip first line
                    count = count + 1
                    continue
                line = line.replace("  ", " ")
                raw_reference[path].append(line.split(' ', 8)[-1])
        else:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={"message": err}
                )
            )
    return raw_reference
    

def is_ssd(rotational):
    if rotational == '0':
        return True
    if rotational == '1':
        return False
    """Rotational attribute not found for
    this device which is not either SSD or HD
    """
    return False
