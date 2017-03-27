from tendrl.commons.event import Event
from tendrl.commons.message import Message

from tendrl.commons.utils import cmd_utils


def get_node_disks():
    rv = {}
    rv["disks"] = []
    rv["free_disks_id"] = []
    rv["used_disks_id"] = []
    disks, err = get_all_disks()
    if err == "":
        columns = 'NAME,KNAME,PKNAME,MAJ:MIN,FSTYPE,MOUNTPOINT,LABEL,' \
                  'UUID,' \
                  'RA,RO,RM,SIZE,STATE,OWNER,GROUP,MODE,ALIGNMENT,' \
                  'MIN-IO,OPT-IO,' \
                  'PHY-SEC,LOG-SEC,ROTA,SCHED,RQ-SIZE,DISC-ALN,' \
                  'DISC-GRAN,DISC-MAX,' \
                  'DISC-ZERO'
        keys = columns.split(',')
        lsblk = (
            "lsblk --all --bytes --noheadings --output='%s' --path --raw" %
            columns)
        cmd = cmd_utils.Command(lsblk)
        out, err, rc = cmd.run()
        if not err:
            devlist = map(
                lambda line: dict(zip(keys, line.split(' '))),
                out.splitlines())
            for disk in disks:
                for dev_info in devlist:
                    if dev_info['NAME'] == disk['device_name']:
                        disk['disk_kernel_name'] = dev_info['KNAME']
                        disk['parent_name'] = dev_info['PKNAME']
                        disk['major_to_minor_no'] = dev_info['MAJ:MIN']
                        disk['fstype'] = dev_info['FSTYPE']
                        disk['mount_point'] = dev_info['MOUNTPOINT']
                        disk['label'] = dev_info['LABEL']
                        disk['fsuuid'] = dev_info['UUID']
                        disk['read_ahead'] = dev_info['RA']
                        if dev_info['RO'] == '0':
                            disk['read_only'] = False
                        else:
                            disk['read_only'] = True
                        if dev_info['RM'] == '0':
                            disk['removable_device'] = False
                        else:
                            disk['removable_device'] = True
                        disk['size'] = dev_info['SIZE']
                        disk['state'] = dev_info['STATE']
                        disk['owner'] = dev_info['OWNER']
                        disk['group'] = dev_info['GROUP']
                        disk['mode'] = dev_info['MODE']
                        disk['alignment'] = dev_info['ALIGNMENT']
                        disk['min_io_size'] = dev_info['MIN-IO']
                        disk['optimal_io_size'] = dev_info['OPT-IO']
                        disk['phy_sector_size'] = dev_info['PHY-SEC']
                        disk['log_sector_size'] = dev_info['LOG-SEC']
                        if disk['disk_type'] == "disk":
                            disk['ssd'] = is_ssd(dev_info['ROTA'])
                        else:
                            disk['ssd'] = False
                        disk['scheduler_name'] = dev_info['SCHED']
                        disk['req_queue_size'] = dev_info['RQ-SIZE']
                        disk['discard_align_offset'] = dev_info[
                            'DISC-ALN']
                        disk['discard_granularity'] = dev_info[
                            'DISC-GRAN']
                        disk['discard_max_bytes'] = dev_info[
                            'DISC-MAX']
                        disk['discard_zeros_data'] = dev_info[
                            'DISC-ZERO']
                        rv['disks'].append(disk)
                        if disk['disk_type'] == "disk":
                            rv['free_disks_id'].append(disk['disk_id'])
                        else:
                            rv['used_disks_id'].append(disk['disk_id'])
        else:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={"message": str(err)}
                )
            )
    else:
        Event(
            Message(
                priority="error",
                publisher=NS.publisher_id,
                payload={"message": str(err)}
            )
        )
    return rv


def get_all_disks():
    disks = []
    # Block will give all disk and partitons and cdroms details
    cmd = cmd_utils.Command('hwinfo --block')
    out, err, rc = cmd.run()
    if not err:
        all_disks = []
        parents = []
        for blocks in out.split('\n\n'):
            devlist = {"disk_id": "",
                       "parent_id": "",
                       "disk_type": "",
                       "model": "",
                       "vendor": "",
                       "serial_no": "",
                       "device_name": "",
                       "sysfs_id": "",
                       "sysfs_busid": "",
                       "sysfs_device_link": "",
                       "driver_modules": "",
                       "driver": "",
                       "device_files": "",
                       "device_number": "",
                       "device": "",
                       "drive_status": "",
                       "rmversion": "",
                       "bios_id": "",
                       "geo_bios_edd": "",
                       "geo_bios_legacy": "",
                       "geo_logical": ""
                       }
            for line in blocks.split('\n'):
                if "Unique ID" in line:
                    devlist["disk_id"] = \
                        line.split(':')[1].lstrip()
                elif "Parent ID" in line:
                    devlist["parent_id"] = \
                        line.split(':')[1].lstrip()
                elif "Hardware Class" in line:
                    devlist["disk_type"] = \
                        line.split(':')[1].lstrip()
                elif "Model" in line:
                    devlist["model"] = \
                        line.split(':')[1].lstrip().replace('"', "")
                elif "Vendor" in line:
                    devlist["vendor"] = \
                        line.split(':')[1].lstrip().replace('"', "")
                elif "Serial ID" in line:
                    devlist["serial_no"] = \
                        line.split(':')[1].lstrip().replace('"', "")
                elif "Device File:" in line:
                    devlist["device_name"] = \
                        line.split(':')[1].lstrip()
                elif "Revision" in line:
                    devlist["rmversion"] = \
                        line.split(':')[1].lstrip().replace('"', "")
                elif "Drive status" in line:
                    devlist["drive_status"] = \
                        line.split(':')[1].lstrip()
                elif "SysFS ID" in line:
                    devlist["sysfs_id"] = \
                        line.split(':')[1].lstrip()
                elif "SysFS BusID" in line:
                    devlist["sysfs_busid"] = \
                        line.split(':')[1].lstrip()
                elif "SysFS Device Link" in line:
                    devlist["sysfs_device_link"] = \
                        line.split(':')[1].lstrip()
                elif "Driver Modules" in line:
                    driver_modules = \
                        line.split(':')[1].lstrip()
                    devlist["driver_modules"] = \
                        driver_modules.replace('"', "").split(', ')
                elif "Driver" in line:
                    driver = line.split(':')[1].lstrip()
                    devlist["driver"] = \
                        driver.replace('"', "").split(', ')
                elif "Device Files" in line:
                    device_files = \
                        line.split(':')[1].lstrip()
                    devlist["device_files"] = \
                        device_files.split(', ')
                elif "Device Number" in line:
                    devlist["device_number"] = \
                        line.split(':')[1].lstrip()
                elif "Device" in line:
                    devlist["device"] = \
                        line.split(':')[1].lstrip().replace('"', "")
                elif "BIOS id" in line:
                    devlist["bios_id"] = \
                        line.split(':')[1].lstrip()
                elif "Geometry (Logical)" in line:
                    devlist["geo_logical"] = \
                        line.split(':')[1].lstrip()
                elif "Geometry (BIOS EDD)" in line:
                    devlist["geo_bios_edd"] = \
                        line.split(':')[1].lstrip()
                elif "Geometry (BIOS Legacy)" in line:
                    devlist["geo_bios_legacy"] = \
                        line.split(':')[1].lstrip()
            if devlist["disk_type"] == "disk":
                all_disks.append(devlist)
            elif devlist["disk_type"] == "partition":
                devlist["used"] = True
                disks.append(devlist)
                parents.append(devlist["parent_id"])
        for disk in all_disks:
            if not disk["disk_id"] in parents:
                disk["used"] = False
                disks.append(disk)
    return disks, err


def is_ssd(rotational):
    if rotational == '0':
        return True
    if rotational == '1':
        return False
    """Rotational attribute not found for
    this device which is not either SSD or HD
    """
    return False
