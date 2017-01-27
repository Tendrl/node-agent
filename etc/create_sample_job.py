import json
import uuid

import etcd

job_id1 = str(uuid.uuid4())

job = {
    "integration_id": "some_uuid",
    "run": "tendrl.node_agent.flows.import_cluster.ImportCluster",
    "status": "new",
    "parameters": {
        "TendrlContext.integration_id": "some_uuid",
        "Node[]": ["9eced8a0-fd46-4144-9578-5b35c2ae2006"],
        "DetectedCluster.sds_pkg_name": "gluster"
    },
    "type": "node",
    "node_ids": ["9eced8a0-fd46-4144-9578-5b35c2ae2006"]
}

print "/queue/%s" % job_id1 
client = etcd.Client(host="your_etcd_api_ip", port=2379)
client.write("/queue/%s" % job_id1, json.dumps(job))
