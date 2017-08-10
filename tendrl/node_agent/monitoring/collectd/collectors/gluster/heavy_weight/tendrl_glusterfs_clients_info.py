import collectd
import sys
import traceback
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree

sys.path.append('/usr/lib64/collectd/gluster')
import utils as tendrl_glusterfs_utils
sys.path.remove('/usr/lib64/collectd/gluster')



CONFIG = {}


def _parseVolumeStatusClients(tree):
    ret_val = []
    for vol in tree.findall('volStatus/volumes/volume'):
        vol_name = vol.find('volName').text
        status = {
            'volume_name': vol_name,
            'bricks': []
        }
        for el in tree.findall('volStatus/volumes/volume/node'):
            hostname = el.find('hostname').text
            path = el.find('path').text
            hostuuid = el.find('peerid').text
            clientsStatus = []
            for c in el.findall('clientsStatus/client'):
                clientValue = {}
                for ch in c.getchildren():
                    clientValue[ch.tag] = ch.text or ''
                clientsStatus.append({'hostname': clientValue['hostname'],
                                      'bytesRead': clientValue['bytesRead'],
                                      'bytesWrite': clientValue['bytesWrite']})
            status['bricks'].append({'brick': '%s:%s' % (hostname, path),
                                     'hostuuid': hostuuid,
                                     'clientsStatus': clientsStatus})
        ret_val.append(status)
    return ret_val


def get_volume_client_info():
    ret_val = {}
    vol_status_clients_info = {}
    vol_status_client_op, vol_status_client_err = \
        tendrl_glusterfs_utils.exec_command(
            "gluster volume status all clients --xml"
        )
    if vol_status_client_err:
        collectd.error(
            'Failed to fetch volume status client info. The error is: %s' % (
                vol_status_client_err
            )
        )
        return ret_val
    try:
        vol_status_clients_info = _parseVolumeStatusClients(
            ElementTree.fromstring(vol_status_client_op)
        )
        return vol_status_clients_info
    except (
        AttributeError,
        KeyError,
        ValueError,
        ElementTree.ParseError
    ):
        collectd.error(
            'Failed to collect client details. Error %s' % (
                traceback.format_exc()
            )
        )
        return ret_val


def read_callback():
    vols_clients_info = get_volume_client_info()
    for vol_client_info in vols_clients_info:
        vol_connections_count = 0
        vol_name = vol_client_info.get('volume_name', '')
        for brick in vol_client_info.get('bricks', []):
            vol_connections_count = vol_connections_count + len(
                brick.get('clientsStatus', [])
            )
        tendrl_glusterfs_utils.write_graphite(
            "clusters.%s.volumes.%s.connections_count" % (
                CONFIG['integration_id'],
                vol_name
            ),
            vol_connections_count,
            CONFIG['graphite_host'],
            CONFIG['graphite_port']
        )


def configure_callback(configobj):
    global CONFIG
    CONFIG = {
        c.key: c.values[0] for c in configobj.children
    }


collectd.register_config(configure_callback)
collectd.register_read(read_callback, 600)
