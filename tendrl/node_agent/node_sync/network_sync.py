import netaddr
import netifaces as ni
from tendrl.commons.utils import cmd_utils
import logging

LOG = logging.getLogger(__name__)


def get_node_network():
    """return
           [{"ipv4": ["ipv4address", ...],
             "ipv6": ["ipv6address, ..."],
             "netmask": ["subnet", ...],
             "subnet": "subnet",
             "status":"up/down",
             "interface_id": "",
             "sysfs_id": "",
             "device_link": "",
             "interface_type": "",
             "model": "",
             "driver_modules": "",
             "drive": "",
             "hw_address": "",
             "link_detected": ""
             }, ...
          ]
    """
    rv = []
    network_interfaces = get_node_interface()
    cmd = cmd_utils.Command('hwinfo --network')
    out, err, rc = cmd.run()
    if not err:
        for interface in out.split('\n\n'):
            devlist = {"interface_id": "",
                       "sysfs_id": "",
                       "device_link": "",
                       "interface_type": "",
                       "model": "",
                       "driver_modules": "",
                       "drive": "",
                       "interface": "",
                       "hw_address": "",
                       "link_detected": ""}
            for line in interface.split('\n'):
                if "Unique ID" in line:
                    devlist['interface_id'] = \
                        line.split(':')[1].lstrip()
                elif "SysFS ID" in line:
                    devlist['sysfs_id'] = \
                        line.split(':')[1].lstrip()
                elif "SysFS Device Link" in line:
                    devlist['device_link'] = \
                        line.split(':')[1].lstrip()
                elif "Hardware Class" in line:
                    devlist['interface_type'] = \
                        line.split(':')[1].lstrip()
                elif "Model" in line:
                    devlist['model'] = \
                        line.split(':')[1].lstrip().replace('"', "")
                elif "Driver Modules" in line:
                    devlist['driver_modules'] = \
                        line.split(':')[1].lstrip().replace('"', "")
                elif "Driver" in line:
                    devlist['driver'] = \
                        line.split(':')[1].lstrip().replace('"', "")
                elif "Device File" in line:
                    devlist['interface'] = \
                        line.split(':')[1].lstrip()
                elif "HW Address" in line:
                    devlist['hw_address'] = \
                        line.split(':')[1].lstrip()
                elif "Link detected" in line:
                    devlist['link_detected'] = \
                        line.split(':')[1].lstrip()
            if devlist["interface"] in network_interfaces:
                interface_name = devlist["interface"]
                network_interfaces[interface_name].update(devlist)
                rv.append(network_interfaces[interface_name])
    else:
        LOG.error(err)

    return rv


def get_node_interface():
    '''returns structure
    {"interface_name": {"ipv4": ["ipv4address", ...],
                        "ipv6": ["ipv6address", ...]
                        "netmask": ["subnet", ...],
                        "subnet": "subnet",
                        "status":"up/down"},...}
    '''
    interfaces = ni.interfaces()
    rv = {}
    invalid = 'lo'
    for interface in interfaces:
        if interface != invalid:
            IPv4 = []
            IPv6 = []
            netmask = []
            subnet = ""
            status, err = Check_interface_status(interface)
            if not err:
                if is_ipv4_present(interface):
                    ipv4_addr_list = ni.ifaddresses(interface)[ni.AF_INET]
                    for ipv4_addr_detail in ipv4_addr_list:
                        IPv4.append(ipv4_addr_detail['addr'])
                        netmask.append(ipv4_addr_detail['netmask'])
                    subnet = get_subnet(IPv4[0], netmask[0])
                if is_ipv6_present(interface):
                    ipv6_addr_list = ni.ifaddresses(interface)[ni.AF_INET6]
                    for ipv6_addr_detail in ipv6_addr_list:
                        IPv6.append(ipv6_addr_detail['addr'])
            else:
                LOG.error(err)

            rv[interface] = (
                {
                    "ipv4": IPv4,
                    "ipv6": IPv6,
                    "netmask": netmask,
                    "subnet": subnet,
                    "status": status
                })
    return rv


def is_ipv4_present(interface):
    addr = ni.ifaddresses(interface)
    return ni.AF_INET in addr


def is_ipv6_present(interface):
    addr = ni.ifaddresses(interface)
    return ni.AF_INET6 in addr


def get_subnet(ipv4, netmask):
    cidr = netaddr.IPNetwork('%s/%s' % (ipv4, netmask))
    network = ("%s/%s") % (str(cidr.network), str(cidr).split('/')[-1])
    return network


def Check_interface_status(interface):
    status = ""
    err = None
    try:
        with open('/sys/class/net/%s/operstate' % interface, 'r') as f:
            status = f.read().strip('\n')
    except IOError as ex:
        err = str(ex)
    return status, err
