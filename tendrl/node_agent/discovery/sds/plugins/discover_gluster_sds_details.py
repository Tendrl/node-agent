import hashlib
import subprocess

from tendrl.commons.utils import log_utils as logger
from tendrl.node_agent.discovery.sds.discover_sds_plugin \
    import DiscoverSDSPlugin


class DiscoverGlusterStorageSystem(DiscoverSDSPlugin):
    def _derive_cluster_id(self):
        cmd = subprocess.Popen(
            "gluster pool list",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = cmd.communicate()
        if err or out is None or "Connection failed" in out:
            _msg = "Could not detect SDS:Gluster installation"
            logger.log(
                "debug",
                NS.publisher_id,
                {"message": _msg}
            )
            return ""
        lines = out.split('\n')[1:]
        gfs_peers_uuid = []
        gfs_peer_data = {}
        for line in lines:
            if line != '':
                peer = line.split()
                # Use the gluster generated pool UUID as unique key
                gfs_peers_uuid.append(peer[0])
                gfs_peer_data[peer[0]] = {"connected": peer[-1],
                                          "hostname": peer[-2]}

        gfs_peers_uuid.sort()
        return (hashlib.sha256("".join(gfs_peers_uuid)).hexdigest(),
                gfs_peer_data)

    def discover_storage_system(self):
        ret_val = {}

        # get the gluster version details
        # form the temporary cluster_id
        cluster_id, gfs_peers = self._derive_cluster_id()
        ret_val['detected_cluster_id'] = cluster_id
        ret_val['detected_cluster_name'] = "gluster-%s" % cluster_id
        ret_val['peers'] = gfs_peers

        cmd = subprocess.Popen(
            "gluster --version",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = cmd.communicate()
        if err and 'command not found' in err:
            logger.log(
                "debug",
                NS.publisher_id,
                {"message": "gluster not installed on host"}
            )
            return ret_val
        lines = out.split('\n')
        if cluster_id:
            ret_val['pkg_version'] = lines[0].split()[1]
            ret_val['pkg_name'] = "gluster"

        return ret_val
