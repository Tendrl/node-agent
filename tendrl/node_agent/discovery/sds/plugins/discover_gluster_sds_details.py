import hashlib
import subprocess

from tendrl.commons.event import Event
from tendrl.commons.message import Message

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
        if err:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={"message": "Error formulating cluster_id"}
                )
            )
            return ""
        lines = out.split('\n')[1:]
        gfs_peers = []
        for line in lines:
            if line != '':
                peer = line.split()
                # Use the gluster generated pool UUID as unique key
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
            Event(
                Message(
                    priority="debug",
                    publisher=NS.publisher_id,
                    payload={"message": "gluster not installed on host"}
                )
            )
            return ret_val
        lines = out.split('\n')
        ret_val['pkg_version'] = lines[0].split()[1]
        ret_val['pkg_name'] = "gluster"

        # form the temporary cluster_id
        cluster_id = self._derive_cluster_id()
        ret_val['detected_cluster_id'] = cluster_id
        ret_val['detected_cluster_name'] = "gluster-%s" % cluster_id

        return ret_val
