import hashlib
import json
import os
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

        # Check if the file /usr/share/glusterfs/release exists.
        # if the file exists, read the version details from this
        if os.path.exists('/usr/share/glusterfs/release'):
            try:
                with open('/usr/share/glusterfs/release') as f:
                    ver_det = f.read().split('\n')[0]
                    ret_val['pkg_name'] = ver_det.split(" ")[0]
                    ret_val['pkg_version'] = ver_det.split(" ")[1]
            except IOError:
                logger.log(
                    "debug",
                    NS.publisher_id,
                    {"message": "Failed to get version details"}
                )
                return ret_val
        else:
            # A sample output from "rpm -qa | grep glusterfs-server"
            # looks as below
            # `glusterfs-server-3.8.4-54.4.el7rhgs.x86_64`
            # In case of upstream build the format could be as below
            # `glusterfs-server-4.1dev-0.203.gitc3e1a2e.el7.centos.x86_64`
            # `glusterfs-server-3.12.8-0.0.el7.centos.x86_64.rpm`
            cmd = subprocess.Popen(
                "rpm -q glusterfs-server",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            out, err = cmd.communicate()
            if out in [None, ""] or err:
                logger.log(
                    "debug",
                    NS.publisher_id,
                    {"message": "gluster not installed on host"}
                )
                return ret_val
            lines = out.split('\n')
            if cluster_id:
                version_det = lines[0].split(
                    'glusterfs-server-'
                )[-1]
                maj_ver = version_det.split('.')[0]
                min_ver = version_det.split('.')[1]
                rel = version_det.split('.')[2]
                build_no = None
                if '-' in rel:
                    build_no = rel.split('-')[1]
                    rel = rel.split('-')[0]
                # Check for rpm version. if its something less than 3.8.4-52
                # its not supported version
                if int(maj_ver) == 3 and int(min_ver) == 8 and \
                    int(rel) == 4 and build_no is not None and \
                    int(build_no) < 52:
                    ret_val['pkg_name'] = 'RHGS'
                    ret_val['pkg_version'] = 'un-supported'
                elif int(maj_ver) == 3 and int(min_ver) == 8 and \
                    int(rel) == 4 and build_no in not None and \
                    int(build_no) >= 52:
                    ret_val ['pkg_name'] = 'RHGS'
                    ret_val[pkg_version] = '3.3.1'
                else:
                    ret_val['pkg_version'] = "%s.%s.%s" % (
                        version_det.split('.')[0],
                        version_det.split('.')[1],
                        version_det.split('.')[2]
                    )
                    ret_val['pkg_name'] = "gluster"

        return ret_val
