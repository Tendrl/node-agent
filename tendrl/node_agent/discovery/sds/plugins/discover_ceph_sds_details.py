import json
import logging
import subprocess

from tendrl.node_agent.discovery.sds.discover_sds_plugin \
    import DiscoverSDSPlugin
from tendrl.node_agent import ini2json

LOG = logging.getLogger(__name__)


class DiscoverCephStorageSystem(DiscoverSDSPlugin):
    def discover_storage_system(self):
        ret_val = {}

        # get the gluster version details
        cmd = subprocess.Popen(
            "ceph --version",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = cmd.communicate()
        if err and 'command not found' in err:
            LOG.info("ceph not installed on host")
            return ret_val

        if out:
            details = out.split()

            ret_val['pkg_version'] = details[2]
            ret_val['pkg_name'] = details[0]

            # get the cluster_id details
            raw_data = ini2json.ini_to_dict("/etc/ceph/ceph.conf")
            if "global" in raw_data:
                ret_val['detected_cluster_id'] = raw_data['global']['fsid']
                ret_val['cluster_attrs'] = {'fsid': raw_data['global']['fsid'],
                                            'name': 'ceph'}

            return ret_val
