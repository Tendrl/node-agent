import json
import uuid

import etcd

job_id1 = str(uuid.uuid4())

job = {
    "run": "node_agent.flows.GenerateJournalMapping",
    "status": "new",
    "parameters": {
        "Cluster.node_configuration": {
            "12367fb3-0074-4b3d-aa90-b9518977987d": {
              "storage_disks": [
                {"device": "/dev/vdb", "size": 10737418240, "ssd": False},
                {"device": "/dev/vdc", "size": 10737418240, "ssd": False},
                {"device": "/dev/vdd", "size": 26843545600, "ssd": True},
              ]
            }
        }
    },
    "type": "node",
    "tags": ["tendrl/monitor"],
    "node_ids": ["88a366b3-c2d7-4076-9256-30538cf93cec"]
}

print("/queue/%s/" % job_id1)
client = etcd.Client(host="localhost", port=2379)
client.write("/queue/%s" % job_id1, None, dir=True)
client.write("/queue/%s/payload" % job_id1, json.dumps(job))
client.write("/queue/%s/status" % job_id1, "new")

