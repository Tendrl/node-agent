import os.path
import subprocess

from tendrl.commons.event import Event
from tendrl.commons.message import Message

from tendrl.node_agent.discovery.sds.discover_sds_plugin \
    import DiscoverSDSPlugin
from tendrl.node_agent import ini2json


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
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={"message": "ceph not installed on host"}
                )
            )
            return ret_val

        if out:
            details = out.split()

            ret_val['pkg_version'] = details[2]
            ret_val['pkg_name'] = details[0]

            # get the cluster_id details
            os_name = NS.platform.os
            cfg_file = ""
            cluster_name = None
            if os_name in ['CentOS Linux', 'Red Hat Enterprise Linux Server']:
                cfg_file = '/etc/sysconfig/ceph'
            # TODO(shtripat) handle the case of ubuntu

            if cfg_file != "":
                if not os.path.exists(cfg_file):
                    Event(
                        Message(
                            priority="info",
                            publisher=NS.publisher_id,
                            payload={"message": "config file: %s not found" %
                                                cfg_file
                                     }
                        )
                    )
                    return ret_val
                with open(cfg_file) as f:
                    for line in f:
                        if line.startswith("CLUSTER="):
                            cluster_name = line.split('\n')[0].split('=')[1]

            if cluster_name:
                raw_data = ini2json.ini_to_dict(
                    "/etc/ceph/%s.conf" % cluster_name
                )
                if "global" in raw_data:
                    ret_val['detected_cluster_id'] = raw_data['global']['fsid']
                    ret_val['detected_cluster_name'] = cluster_name

            return ret_val
