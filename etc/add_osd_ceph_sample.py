import json
import uuid

import etcd

payload = {
    "run": "integrations.ceph.flows.AddOsds",
    "type": "node",
    "created_at": "2017-03-09T14:15:14Z",
    "username": "admin",
    "parameters": {
        "TendrlContext.cluster_name": "MyCluster",
        "TendrlContext.cluster_id": "140cd3d5-58e4-4935-a954-d946ceff371d",
        "Cluster.public_network": "10.70.40.0/22",
        "Cluster.cluster_network": "10.70.40.0/22",
        "Cluster.node_configuration": {
            "4d3fbbdb-f0d1-4f1e-a804-67dcf910601e": {
                "role": "ceph/osd",
                "provisioning_ip": "{ip-1}",
                "journal_size": 5120,
                "journal_colocation": False,
                "storage_disks": [{
                    "device": "/dev/vdf",
                    "journal": "/dev/vdg"
                }
                ]
            },
        },
        "TendrlContext.integration_id": "89604c6b-2eff-4221-96b4-e41319240240"
    },
    "tags": ["provisioner/ceph"]
}

job_id1 = str(uuid.uuid4())

print("/queue/%s/" % job_id1)
client = etcd.Client(host="localhost", port=2379)
client.write("/queue/%s" % job_id1, None, dir=True)
client.write("/queue/%s/payload" % job_id1, json.dumps(payload))
client.write("/queue/%s/status" % job_id1, "new")
