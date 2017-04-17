
import json
import socket

import urllib3

from tendrl.node_agent.provisioner.ceph.provisioner_base import\
    ProvisionerBasePlugin
from tendrl.node_agent.provisioner.ceph import utils as \
    provisioner_utils


class CephInstallerPlugin(ProvisionerBasePlugin):

    _MGET = 'GET'
    _MPOST = 'POST'
    _CEPH_INSTALLER_API_PORT = '8181'

    def __init__(
        self,
    ):
        self.http = urllib3.PoolManager()
        self.monitor_secret = provisioner_utils.generate_auth_key()

    def set_provisioner_node(self, provisioner_node):
        self.provisioner_node = provisioner_node

    def install_mon(self, mons):
        url = 'http://localhost:%s/api/mon/install' % \
            self._CEPH_INSTALLER_API_PORT

        # Sample payload for mon install API is
        # Content-Type: application/json
        # {
        #     "calamari": false,
        #     "hosts": ["mon1.example.com", "mon2.example.com", ...],
        #     "redhat_storage": false,
        #     "redhat_use_cdn": true,
        #     "verbose": false,
        # }

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

        # Sample payload for osd install API is
        # Content-Type: application/json
        # {
        #     "hosts": ["osd1.example.com", "osd2.example.com"],
        #     "redhat_storage": false,
        #     "redhat_use_cdn": true,
        #     "verbose": false,
        # }

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
                raise Exception('Server response was not valid JSON: %r' % e)
            return res_data['identifier']
        else:
            return None

    def configure_mon(
        self,
        host,
        cluster_id,
        cluster_name,
        ip_address,
        cluster_network,
        public_network,
        monitors
    ):
        url = 'http://localhost:%s/api/mon/configure' % \
            self._CEPH_INSTALLER_API_PORT

        # Sample payload for osd install API is
        # Content-Type: application/json
        # {
        #     "calamari": false,
        #     "conf": {"global": {"auth supported": "cephx"}},
        #     "host": "mon1.example.com",
        #     "interface": "eth0",
        #     "fsid": "deedcb4c-a67a-4997-93a6-92149ad2622a",
        #     "monitor_secret": "AQA7P8dWAAAAABAAH/tbiZQn/40Z8pr959UmEA==",
        #     "cluster_name": "my-ceph-cluster",
        #     "cluster_network": "192.0.2.0/24",
        #     "public_network": "198.51.100.0/24",
        #     "monitors": [{"host": "mon0.host", "interface": "eth0"}],
        #     "redhat_storage": false,
        #     "verbose": false,
        # }
        #
        # Note: monitors array is optional. This is only optional when no
        # other monitors currently exist in the cluster. If you are configuring
        # a mon for an existing cluster, provide a list of objects representing
        # the monitor host and its interface or address.

        data = {
            "calamari": False,
            "host": host,
            "address": ip_address,
            "fsid": cluster_id,
            "monitor_secret": self.monitor_secret,
            "cluster_name": cluster_name,
            "cluster_network": cluster_network,
            "public_network": public_network,
            "redhat_storage": False,
            "verbose": False
        }
        if monitors is not None:
            data.update({"monitors": monitors})
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

    def configure_osd(
        self,
        host,
        devices,
        cluster_id,
        cluster_name,
        journal_size,
        cluster_network,
        public_network,
        monitors
    ):
        url = 'http://localhost:%s/api/osd/configure' % \
            self._CEPH_INSTALLER_API_PORT

        # Sample payload for osd install API is
        # Content-Type: application/json
        # {
        #     "conf": {"global": {"auth supported": "cephx"}},
        #     "devices": {"/dev/sdb":"/dev/sdc"},
        #     "fsid": "deedcb4c-a67a-4997-93a6-92149ad2622a",
        #     "host": "osd1.example.com",
        #     "journal_size": 1024,
        #     "cluster_name": "my-ceph-cluster",
        #     "cluster_network": "192.0.2.0/24",
        #     "public_network": "198.51.100.0/24",
        #     "redhat_storage": false,
        #     "monitors": [
        #          {
        #              "host": "mon0.host", "interface": "eth1"},
        #              {"host": "mon1.host", "address": "10.0.0.1"
        #          }
        #     ],
        #     "verbose": false,
        # }
        #
        # Note: devices is a mandatory parameter. A mapping of OSD device to
        # Journal like device: {"device": "journal"} (when the journal is
        # separate from the OSD) or ["/dev/sdb", "/dev/sdc"] for collocated
        # OSDs and Journals.

        data = {
            "devices": devices,
            "host": host,
            "fsid": cluster_id,
            "journal_size": journal_size,
            "cluster_name": cluster_name,
            "cluster_network": cluster_network,
            "public_network": public_network,
            "monitors": monitors,
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
                # Sample response from tasks/{id} api is
                # Content-Type: application/json
                # {
                #     "command": "command arguments flags sample",
                #     "ended": "2016-01-27T15:03:23.438172",
                #     "endpoint": "/api/rgw/configure",
                #     "id": "2207bde6-4346-4a83-984a-40a5c00056c1",
                #     "started": "2016-01-27T15:03:22.638173",
                #     "stderr": "command stderr",
                #     "stdout": "command stdout"
                # }

                res_data = json.loads(resp.data.decode('utf-8'))
                return res_data
        else:
            return None

    def setup(self):
        url = 'http://%s:%s/setup/' % (socket.gethostbyname(
            socket.gethostname()), self._CEPH_INSTALLER_API_PORT)
        resp = self.http.request(
            self._MGET,
            url)
        if resp.status == 200:
            resp_data = resp.data.decode("utf-8")
            return resp_data
