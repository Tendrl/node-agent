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
    "sds_type": "ceph",
    "sds_version": "10.2.5",
    "name": "MyCluster",
        "fsid": "140cd3d5-58e4-4935-a954-d946ceff371d",
        "public_network": "10.70.40.0/22",
        "cluster_network": "10.70.40.0/22",
        "ceph_conf_overrides": {
            "global": {
                "osd_pool_default_pg_num": 128,
                "pool_default_pgp_num": 1
            }
        },
    "node_configuration": {
        "81720b6c-6732-49dd-ad32-15845f199c79": {
            "role": "ceph/mon",
            "provisioning_ip": "10.70.43.3",
            "monitor_interface": "eth0"
        },
        "ab003bbc-00cd-4b74-b236-f19c2c33b96b": {
            "role": "ceph/osd",
            "provisioning_ip": "10.70.42.183",
            "journal_size": 5192,
            "journal_colocation": False,
            "storage_disks": [{
                "device": "/dev/vdb",
                "journal": "/dev/vdc"
            }
            ]
        },
    },
    "TendrlContext.integration_id": "89604c6b-2eff-4221-96b4-e41319240240"
},
"node_ids": [],
"tags": ["provisioner/ceph"]
}

import json
import uuid

import etcd

job_id1 = str(uuid.uuid4())


print("/queue/%s/" % job_id1)
client = etcd.Client(host="10.70.42.161", port=2379)
client.write("/queue/%s" % job_id1, None, dir=True)
client.write("/queue/%s/payload" % job_id1, json.dumps(payload))
client.write("/queue/%s/status" % job_id1, "new")
