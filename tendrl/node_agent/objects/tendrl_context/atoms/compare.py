import json

from tendrl.commons.atoms.base_atom import BaseAtom


class Compare(BaseAtom):
    def run(self, parameters):
        sds_name = parameters.get("Tendrl_context.sds_name")
        sds_version = parameters.get("Tendrl_context.sds_version")
        return True

        client = parameters['etcd_server']
        # get the node-agent_key some how
        # for now reading it from the json file

        with open("/etc/tendrl/tendrl-node-inventory.json") as f:
            j = json.loads(f.read())
            node_uuid = j["node_uuid"]

        path = "/nodes/%s/tendrl_context" % node_uuid
        tendrl_context = client.read(path)
        etcd_sds_name = ""
        etcd_sds_version = ""
        for el in tendrl_context.children:
            if el.key.split('/')[-1] == "sds_name":
                etcd_sds_name = el.value
            if el.key.split('/')[-1] == "sds_version":
                etcd_sds_version = el.value
        status = parameters.get("status")
        if etcd_sds_version == sds_version and etcd_sds_name == sds_name:
            status.append(
                ("Compare",
                 "Sds version and sds names are matched successfully")
            )
        else:
            status.append(
                ("Compare",
                 "Sds version and sds names do not match")
            )
        return status
