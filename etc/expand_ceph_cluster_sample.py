import json
import uuid

import etcd

job_id1 = str(uuid.uuid4())

job = {
    "run": "tendrl.flows.ExpandCluster",
    "status": "new",
    "parameters": {
        "TendrlContext.integration_id": "89604c6b-2eff-4221-96b4-e41319240240",
        "TendrlContext.cluster_name": "MyCluster",
        "TendrlContext.cluster_id": "140cd3d5-58e4-4935-a954-d946ceff371d",
        "TendrlContext.sds_name": "ceph",
        "Node[]": ["9a811957-94fa-43f4-9605-efd40335b31a",
                   "d41d073f-db4e-4abf-8018-02b30254b912"],
        "Cluster.public_network": "10.70.40.0/22",
        "Cluster.cluster_network": "10.70.40.0/22",
        "Cluster.node_configuration": {
            "9a811957-94fa-43f4-9605-efd40335b31a": {
                "role": "ceph/mon",
                "provisioning_ip": "{ip-1}",
                "monitor_interface": "eth0"
            },
            "d41d073f-db4e-4abf-8018-02b30254b912": {
                "role": "ceph/osd",
                "provisioning_ip": "{ip-2}",
                "journal_size": 5120,
                "journal_colocation": False,
                "storage_disks": [
                    {"device": "/dev/vdb", "journal": "/dev/vdc"},
                    {"device": "/dev/vdd", "journal": "/dev/vde"},
                ]
            }
        }
    },
    "type": "node",
    "tags": ["provisioner/ceph"]
}

print("/queue/%s/" % job_id1)
client = etcd.Client(host="localhost", port=2379)
client.write("/queue/%s" % job_id1, None, dir=True)
client.write("/queue/%s/payload" % job_id1, json.dumps(job))
client.write("/queue/%s/status" % job_id1, "new")

