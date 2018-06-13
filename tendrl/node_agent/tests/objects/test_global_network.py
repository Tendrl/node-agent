from mock import patch

from tendrl.commons import objects
from tendrl.node_agent.objects.global_network import GlobalNetwork


@patch.object(objects.BaseObject, "load_definition")
def test_global_network(load_definition):
    load_definition.return_value = {}
    obj = GlobalNetwork(
        interface="eth0",
        interface_id="1",
        ipv4=["127.0.0.1"],
        ipv6=["fe80::219:4aff:fe16:122%eth0"],
        netmask=["255.255.255.0"],
        subnet="127.0.0.1/22",
        status="up",
        sysfs_id="/class/net/eth0",
        device_link="/devices/pci0000",
        interface_type="network interface",
        model="Ethernet network interface"
    )
    out = [{'dir': False,
            'name': 'interface_type',
            'key': '/networks/127.0.0.1_22/1/1/interface_type',
            'value': 'network interface'
            },
           {'dir': False,
            'name': 'device_link',
            'key': '/networks/127.0.0.1_22/1/1/device_link',
            'value': '/devices/pci0000'
            },
           {'dir': False,
            'name': 'interface',
            'key': '/networks/127.0.0.1_22/1/1/interface',
            'value': 'eth0'
            },
           {'dir': False,
            'name': 'model',
            'key': '/networks/127.0.0.1_22/1/1/model',
            'value': 'Ethernet network interface'
            },
           {'dir': False,
            'name': 'interface_id',
            'key': '/networks/127.0.0.1_22/1/1/interface_id',
            'value': '1'
            },
           {'dir': False,
            'name': 'ipv4',
            'key': '/networks/127.0.0.1_22/1/1/ipv4',
            'value': ['127.0.0.1']
            },
           {'dir': False,
            'name': 'ipv6',
            'key': '/networks/127.0.0.1_22/1/1/ipv6',
            'value': ['fe80::219:4aff:fe16:122%eth0']
            },
           {'dir': False,
            'name': 'link_detected',
            'key': '/networks/127.0.0.1_22/1/1/link_detected',
            'value': ''
            },
           {'dir': False,
            'name': 'sysfs_id',
            'key': '/networks/127.0.0.1_22/1/1/sysfs_id',
            'value': '/class/net/eth0'
            },
           {'dir': False,
            'name': 'drive',
            'key': '/networks/127.0.0.1_22/1/1/drive',
            'value': ''
            },
           {'dir': False,
            'name': 'hw_address',
            'key': '/networks/127.0.0.1_22/1/1/hw_address',
            'value': ''
            },
           {'dir': False,
            'name': 'subnet',
            'key': '/networks/127.0.0.1_22/1/1/subnet',
            'value': '127.0.0.1/22'
            },
           {'dir': False,
            'name': 'status',
            'key': '/networks/127.0.0.1_22/1/1/status',
            'value': 'up'
            },
           {'dir': False,
            'name': 'driver_modules',
            'key': '/networks/127.0.0.1_22/1/1/driver_modules',
            'value': ''
            },
           {'dir': False,
            'name': 'driver',
            'key': '/networks/127.0.0.1_22/1/1/driver',
            'value': ''
            },
           {'dir': False,
            'name': 'netmask',
            'key': '/networks/127.0.0.1_22/1/1/netmask',
            'value': ['255.255.255.0']
            },
           {'key': '/networks/127.0.0.1_22/1/1/hash',
            'name': 'hash',
            'dir': False,
            'value': 'd6813b49e3ef0c95a9a46e1121ee42f3'
            },
           {'key': '/networks/127.0.0.1_22/1/1/updated_at',
            'name': 'updated_at',
            'dir': False,
            'value': ''
            }]
    for attr in obj.render():
        if attr["name"] != "hash" and attr not in out:
            raise AssertionError()
