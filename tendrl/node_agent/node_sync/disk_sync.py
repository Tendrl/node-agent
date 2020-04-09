import os

from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.utils import cmd_utils
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger


def sync():
    try:
        _keep_alive_for = int(NS.config.data.get("sync_interval", 10)) + 250
        disks = get_node_disks()
        disk_map = {}
        for disk in disks:
            # Creating dict with disk name as key and disk_id as value
            # It will help populate block device disk_id attribute
            _map = dict(disk_id=disks[disk]['disk_id'], ssd=False)
            disk_map[disks[disk]['disk_name']] = _map
        block_devices = get_node_block_devices(disk_map)

        for disk in disks:
            if disk_map[disks[disk]['disk_name']]:
                disks[disk]['ssd'] = disk_map[disks[disk][
                    'disk_name']]['ssd']

            if "virtio" in disks[disk]["driver"]:
                # Virtual disk
                NS.tendrl.objects.VirtualDisk(**disks[disk]).save(
                    ttl=_keep_alive_for
                )
            else:
                # physical disk
                NS.tendrl.objects.Disk(**disks[disk]).save(ttl=_keep_alive_for)

        for device in block_devices['all']:
            NS.tendrl.objects.BlockDevice(**device).save(ttl=_keep_alive_for)
        for device_id in block_devices['used']:
            etcd_utils.write(
                "nodes/%s/LocalStorage/BlockDevices/used/%s" %
                (NS.node_context.node_id,
                 device_id.replace("/", "_").replace("_", "", 1)),
                device_id, ttl=_keep_alive_for
            )
        for device_id in block_devices['free']:
            etcd_utils.write(
                "nodes/%s/LocalStorage/BlockDevices/free/%s" %
                (NS.node_context.node_id,
                 device_id.replace("/", "_").replace("_", "", 1)),
                device_id, ttl=_keep_alive_for
            )
        raw_reference = get_raw_reference()
        etcd_utils.write(
            "nodes/%s/LocalStorage/DiskRawReference" %
            NS.node_context.node_id,
            raw_reference,
            ttl=_keep_alive_for,
        )
    except(Exception, KeyError) as ex:
        _msg = "node_sync disks sync failed: " + ex.message
        Event(
            ExceptionMessage(
                priority="error",
                publisher=NS.publisher_id,
                payload={"message": _msg,
                         "exception": ex}
            )
        )


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
                        _name = partition.split(':')[1].lstrip()
                        devlist["partition_name"] = \
                            "".join(_name.split(" ")[0])
                    if key.strip() == "Device Files":
                        devlist["device_files"] = \
                            partition.split(':')[1].lstrip()
                    if key.strip() == "Config Status":
                        devlist["config_status"] = \
                            partition.split(':')[1].lstrip()
                # checking if partition parent id is in collected
                # disk_ids or not
                if devlist["parent_hardware_id"] in disks_map:
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
                        disk.split(':')[1].replace(" ", "").replace('"', "")
                elif key.strip() == "Device":
                    devlist["device"] = \
                        disk.split(':')[1].replace(" ", "").replace('"', "")
                elif key.strip() == "Revision":
                    devlist["rmversion"] = \
                        disk.split(':')[1].lstrip().replace('"', "")
                elif key.strip() == "Serial ID":
                    devlist["serial_no"] = \
                        disk.split(':')[1].replace(" ", "").replace('"', "")
                elif key.strip() == "Driver":
                    devlist["driver"] = \
                        disk.split(':')[1].lstrip().replace('"', "")
                elif key.strip() == "Driver Modules":
                    devlist["driver_modules"] = \
                        disk.split(':')[1].lstrip().replace('"', "")
                elif key.strip() == "Device File":
                    _name = disk.split(':')[1].lstrip()
                    devlist["disk_name"] = \
                        "".join(_name.split(" ")[0])
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
                                      devlist["device"] + "_" + devlist[
                    "serial_no"])
            else:
                devlist['disk_id'] = devlist['disk_name']
            if devlist["disk_id"] in disks.keys():
                # Multipath is like multiple I/O paths between
                # server nodes and storage arrays into a single device
                # If single device is connected with more than one path
                # then hwinfo and lsblk will give same device details with
                # different device names. To avoid this duplicate entry,
                # If multiple devices exists with same disk_id then
                # device_name which is lower in alphabetical order is stored.
                # It will avoid redundacy of disks and next sync it will
                # make sure same device detail is populated
                if devlist["disk_name"] < disks[
                        devlist['disk_id']]['disk_name']:
                    disks[devlist["disk_id"]] = devlist
                    disks_map[devlist['hardware_id']] = devlist["disk_id"]
            else:
                disks[devlist["disk_id"]] = devlist
                disks_map[devlist['hardware_id']] = devlist["disk_id"]
    return disks, disks_map, err


def get_node_block_devices(disks_map):
    block_devices = dict(all=list(), free=list(), used=list())
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
        # iterate over the output of lsblk with specfic set of columns
        # and create a list dictornaries mapped with the specfic columns.
        devlist = [dict(zip(keys, line.split(' '))) \
                   for line in out.splitlines()]
        all_parents = []
        parent_ids = []
        multipath = {}
        for dev_info in devlist:
            device = dict()
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
                # if partition is under multipath then parent of multipath
                # is assigned
                if dev_info['PKNAME'] in list(multipath.keys()):
                    dev_info['PKNAME'] = multipath[dev_info['PKNAME']]
                if dev_info['PKNAME'] in disks_map.keys():
                    device['disk_id'] = disks_map[
                        dev_info['PKNAME']]['disk_id']
                    block_devices['all'].append(device)
                    block_devices['used'].append(device['device_name'])

            if dev_info['TYPE'] == 'disk':
                if dev_info['NAME'] in disks_map.keys():
                    device['disk_id'] = disks_map[dev_info['NAME']]['disk_id']
                    disks_map[dev_info['NAME']]['ssd'] = device['ssd']
                    all_parents.append(device)
            if dev_info['TYPE'] == 'mpath':
                multipath[device['device_kernel_name']] = dev_info['PKNAME']
            else:
                if dev_info['PKNAME'] in multipath.keys():
                    dev_info['PKNAME'] = multipath[dev_info['PKNAME']]
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
        logger.log(
            "debug",
            NS.publisher_id,
            {"message": err}
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
            logger.log(
                "debug",
                NS.publisher_id,
                {"message": err}
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
