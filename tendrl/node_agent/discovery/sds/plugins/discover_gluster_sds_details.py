import collections
import hashlib
import logging
import socket
import subprocess

from tendrl.node_agent.discovery.sds.discover_sds_plugin \
    import DiscoverSDSPlugin

LOG = logging.getLogger(__name__)


class DiscoverGlusterStorageSystem(DiscoverSDSPlugin):
    def _derive_cluster_id(self):
        cmd = subprocess.Popen(
            "gluster pool list",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = cmd.communicate()
        if err:
            LOG.error("Error formulating cluster_id")
            return ""
        lines = out.split('\n')[1:]
        gfs_peers = []
        for line in lines:
            if line != '':
                peer = line.split()              
                gfs_peers.append(peer[0])
                
        gfs_peers.sort()
        return hashlib.sha256("".join(gfs_peers)).hexdigest()

    def discover_storage_system(self):
        ret_val = {}

        # get the gluster version details
        cmd = subprocess.Popen(
            "gluster --version",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = cmd.communicate()
        if err and 'command not found' in err:
            LOG.info("gluster not installed on host")
            return ret_val
        lines = out.split('\n')
        ret_val['pkg_version'] = lines[0].split()[1]
        ret_val['pkg_name'] = lines[0].split()[0]

        # form the temporary cluster_id
        ret_val['detected_cluster_id'] = self._derive_cluster_id()
        ret_val['cluster_attrs'] = {}

        return ret_val
