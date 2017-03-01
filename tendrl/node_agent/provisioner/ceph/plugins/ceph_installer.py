
import json
import logging
import urllib3

from tendrl.node_agent.provisioner.ceph.provisioner_base import\
    ProvisionerBasePlugin

LOG = logging.getLogger(__name__)


class CephInstallerPlugin(ProvisionerBasePlugin):

    _MGET = 'GET'
    _MPOST = 'POST'
    _CEPH_INSTALLER_API_PORT = '8181'

    def __init__(
        self,
    ):
        self.http = urllib3.PoolManager()

    def set_provisioner_node(self, provisioner_node):
        self.provisioner_node = provisioner_node

    def install_mon(self, mons):
        url = 'http://localhost:%s/api/mon/install' % \
            self._CEPH_INSTALLER_API_PORT
        data = {
            "calamari": False,
            "hosts": mons,
            "redhat_storage": False,
            "redhat_use_cdn": True,
            "verbose": False,
        }
        resp = self.http.request(
            self._MPOST,
            url,
            body=json.dumps(data),
            headers={'Content-Type': 'application/json'})
        if resp.status == 200:
            try:
                res_data = json.loads(resp.data.decode('utf-8'))
            except (TypeError, ValueError, UnicodeError) as e:
                raise Exception(
                    'Server response was not valid JSON: %r' % e)
            return res_data['identifier']
        else:
            return None

    def install_osd(self, osds):
        url = 'http://localhost:%s/api/osd/install' % \
            self._CEPH_INSTALLER_API_PORT
        data = {
            "hosts": osds,
            "redhat_storage": False,
            "redhat_use_cdn": True,
            "verbose": False,
        }
        resp = self.http.request(
            self._MPOST,
            url,
            body=json.dumps(data),
            headers={'Content-Type': 'application/json'})
        if resp.status == 200:
            try:
                res_data = json.loads(resp.data.decode('utf-8'))
            except (TypeError, ValueError, UnicodeError) as e:
                raise Exception(
                   'Server response was not valid JSON: %r' % e)
            return res_data['identifier']
        else:
            return None

    def configure_mon(self, host, cluster_id, cluster_name, cluster_network, public_network, mons):
        url = 'http://localhost:%s/api/mon/configure' % \
            self._CEPH_INSTALLER_API_PORT
        data = {
            "calamari": False,
            "conf": {"global": {"auth supported": "cephx"}},
            "host": host,
            "interface": "eth0",
            "fsid": cluster_id,
            "monitor_secret": "AQA7P8dWAAAAABAAH/tbiZQn/40Z8pr959UmEA==",
            "cluster_name": cluster_name,
            "cluster_network": cluster_network,
            "public_network": public_network,
            "redhat_storage": False,
            "verbose": False
        }
        if mons is not None:
            data.update({"mons": mons})
        resp = self.http.request(
            self._MPOST,
            url,
            body=json.dumps(data),
            headers={'Content-Type': 'application/json'})
        if resp.status == 200:
            try:
                res_data = json.loads(resp.data.decode('utf-8'))
            except (TypeError, ValueError, UnicodeError) as e:
                raise Exception(
                    'Server response was not valid JSON: %r' % e)
            return res_data['identifier']
        else:
            return None

    def configure_osd(self, host, devices, cluster_id, cluster_name, journal_size, cluster_network, public_network, mons):
        url = 'http://localhost:%s/api/osd/configure' % \
            self._CEPH_INSTALLER_API_PORT
        data = {
            "conf": {"global": {"auth supported": "cephx"}},
            "devices": devices,
            "host": host,
            "fsid": cluster_id,
            "journal_size": journal_size,
            "cluster_name": cluster_name,
            "cluster_network": cluster_network,
            "public_network": public_network,
            "monitors": mons,
            "redhat_storage": False,
            "verbose": False
        }
        resp = self.http.request(
            self._MPOST,
            url,
            body=json.dumps(data),
            headers={'Content-Type': 'application/json'})
        if resp.status == 200:
            try:
                res_data = json.loads(resp.data.decode('utf-8'))
            except (TypeError, ValueError, UnicodeError) as e:
                raise Exception(
                    'Server response was not valid JSON: %r' % e)
            return res_data['identifier']
        else:
            return None

    def task_status(self, task_id):
        url = 'http://localhost:%s/api/tasks/%s' % (
            self._CEPH_INSTALLER_API_PORT, task_id)
        resp = self.http.request(
            self._MGET,
            url)
        if resp.status == 200:
            try:
                res_data = json.loads(resp.data.decode('utf-8'))
            except (TypeError, ValueError, UnicodeError) as e:
                raise Exception(
                    'Server response was not valid JSON: %r' % e)
            return res_data
        else:
            return None
