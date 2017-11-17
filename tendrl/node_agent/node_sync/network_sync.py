import etcd
import netaddr
import netifaces as ni

from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.message import Message
from tendrl.commons.utils import cmd_utils


def sync():
    try:
        _keep_alive_for = int(NS.config.data.get("sync_interval", 10)) + 250
        interfaces = get_node_network()
        if len(interfaces) > 0:
            for interface in interfaces:
                NS.tendrl.objects.NodeNetwork(**interface).save(
                    ttl=_keep_alive_for
                )
                if interface['ipv4']:
                    for ipv4 in interface['ipv4']:
                        index_key = "/indexes/ip/%s" % ipv4
                        try:
                            NS._int.wclient.write(
                                index_key, NS.node_context.node_id,
                                prevExist=False)
                        except etcd.EtcdAlreadyExist:
                            pass
                            # TODO(team) add ipv6 support
                            # if interface['ipv6']:
                            #    for ipv6 in interface['ipv6']:
                            #        index_key = "/indexes/ip/%s/%s" % (ipv6,
                            #
                            # NS.node_context.node_id)
                            #        NS._int.wclient.write(index_key, 1)

        # global network
        if len(interfaces) > 0:
            for interface in interfaces:
                if interface["subnet"] is not "":
                    NS.node_agent.objects.GlobalNetwork(
                        **interface).save(ttl=_keep_alive_for)
        try:
            networks = NS._int.client.read("/networks")
            for network in networks.leaves:
                try:
                    # it will delete any node with empty network detail in
                    # subnet, if one entry present then deletion never happen
                    NS._int.wclient.delete("%s/%s" % (network.key,
                                                      NS.node_context.node_id),
                                           dir=True)
                    # it will delete any subnet dir when it is empty
                    # if one entry present then deletion never happen
                    NS._int.wclient.delete(network.key, dir=True)
                except (etcd.EtcdKeyNotFound, etcd.EtcdDirNotEmpty):
                    continue
        except etcd.EtcdKeyNotFound as ex:
            Event(
                ExceptionMessage(
                    priority="debug",
                    publisher=NS.publisher_id,
                    payload={"message": "Given key is not present in "
                                        "etcd .",
                             "exception": ex
                             }
                )
            )
    except Exception as ex:
        _msg = "node_sync networks sync failed: " + ex.message
        Event(
            ExceptionMessage(
                priority="error",
                publisher=NS.publisher_id,
                payload={"message": _msg,
                         "exception": ex}
            )
        )


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
    if (not err) or "vdsmdummy: command not found" in err:
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
        Event(
            Message(
                priority="debug",
                publisher=NS.publisher_id,
                payload={"message": err}
            )
        )

    return rv


def get_node_interface():
    """returns structure

    {"interface_name": {"ipv4": ["ipv4address", ...],
                        "ipv6": ["ipv6address", ...]
                        "netmask": ["subnet", ...],
                        "subnet": "subnet",
                        "status":"up/down"},...}

    """

    interfaces = ni.interfaces()
    rv = {}
    invalid = 'lo'
    for interface in interfaces:
        if interface != invalid:
            ipv4 = []
            ipv6 = []
            netmask = []
            subnet = ""
            status, err = check_interface_status(interface)
            if not err:
                if is_ipv4_present(interface):
                    ipv4_addr_list = ni.ifaddresses(interface)[ni.AF_INET]
                    for ipv4_addr_detail in ipv4_addr_list:
                        ipv4.append(ipv4_addr_detail['addr'])
                        netmask.append(ipv4_addr_detail['netmask'])
                    subnet = get_subnet(ipv4[0], netmask[0])
                if is_ipv6_present(interface):
                    ipv6_addr_list = ni.ifaddresses(interface)[ni.AF_INET6]
                    for ipv6_addr_detail in ipv6_addr_list:
                        ipv6.append(ipv6_addr_detail['addr'])
            else:
                Event(
                    Message(
                        priority="debug",
                        publisher=NS.publisher_id,
                        payload={"message": err}
                    )
                )

            rv[interface] = (
                {
                    "ipv4": ipv4,
                    "ipv6": ipv6,
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
    network = "%s/%s" % (str(cidr.network), str(cidr).split('/')[-1])
    return network


def check_interface_status(interface):
    status = "unknown"
    err = None
    try:
        with open('/sys/class/net/%s/operstate' % interface, 'r') as f:
            status = f.read().strip('\n')
    except IOError as ex:
        err = str(ex)
    return status, err
