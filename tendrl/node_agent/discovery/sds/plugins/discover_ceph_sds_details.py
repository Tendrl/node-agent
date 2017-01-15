import json
import logging
import subprocess

from tendrl.node_agent.discovery.sds.discover_sds_plugin \
    import DiscoverSDSPlugin

LOG = logging.getLogger(__name__)


class DiscoverCephStorageSystem(DiscoverSDSPlugin):
    def discover_storage_system(self):
        ret_val = {}

        # get the gluster version details
        cmd = subprocess.Popen(
            "ceph version -f json",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = cmd.communicate()
        if err and 'command not found' in err:
            LOG.info("ceph not installed on host")
            return ret_val
        details = json.loads(out)
        ret_val['pkg_version'] = details['version'].split()[2]
        ret_val['pkg_name'] = details['version'].split()[0]

        # get the cluster_id details
        cmd = subprocess.Popen(
            "ceph -s -f json",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = cmd.communicate()
        if err:
            LOG.error("Erro getting cluster details")
            return ret_val
        details = json.loads(out)
        ret_val['detected_cluster_id'] = details['fsid']
        ret_val['cluster_attrs'] = {'fsid': details['fsid'], 'name': 'ceph'}

        return ret_val
