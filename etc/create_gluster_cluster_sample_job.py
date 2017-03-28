payload = {
    "integration_id": "89604c6b-2eff-4221-96b4-e41319240240",
    "run": "tendrl.flows.CreateCluster",
    "type": "node",
    "created_from": "API",
    "created_at": "2017-03-09T14:15:14Z",
    "username": "admin",
    "parameters": {
        "Node[]": ["81720b6c-6732-49dd-ad32-15845f199c79",
                   "ab003bbc-00cd-4b74-b236-f19c2c33b96b"],
        "TendrlContext.sds_name": "glusterfs",
        "TendrlContext.sds_version": "3.2.1",
        "TendrlContext.cluster_name": "MyCluster",
        "TendrlContext.cluster_id": "140cd3d5-58e4-4935-a954-d946ceff371d",
        "Cluster.public_network": "10.70.40.0/22",
        "Cluster.cluster_network": "10.70.40.0/22",
        "Cluster.node_configuration": {
            "ab003bbc-00cd-4b74-b236-f19c2c33b96b": {
                "role": "glusterfs/node",
                "provisioning_ip": "10.70.42.183",
            },
        },
        "TendrlContext.integration_id": "89604c6b-2eff-4221-96b4-e41319240240"
    },
    "node_ids": [],
    "tags": ["provisioner/gluster"]
}

import json
import uuid

import etcd

job_id1 = str(uuid.uuid4())


print("/queue/%s/" % job_id1)
client = etcd.Client(host="hostname", port=2379)
client.write("/queue/%s" % job_id1, None, dir=True)
client.write("/queue/%s/payload" % job_id1, json.dumps(payload))
client.write("/queue/%s/status" % job_id1, "new")
