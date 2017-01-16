import logging
import os
import os.path
import uuid

import etcd

from tendrl.commons.utils import cmd_utils

LOG = logging.getLogger(__name__)
NODE_CONTEXT = "/etc/tendrl/node-agent/node_context"


def get_local_node_context():
    # check if valid uuid is already present in local node_context
    # (/etc/tendrl/node-agent/node_context, if not present generate one and
    # update the file
    if os.path.isfile(NODE_CONTEXT):
        with open(NODE_CONTEXT) as f:
            node_id = f.read()
            if node_id:
                LOG.info("Local Node_context.node_id==%s found!" % node_id)
                return node_id
    else:
        return None


def set_local_node_context():
    node_id = get_local_node_context()
    if node_id is None:
        with open(NODE_CONTEXT, 'wb+') as f:
            node_id = str(uuid.uuid4())
            f.write(node_id)
            LOG.info("Local Node_context.node_id==%s created!" % node_id)

    return node_id


def delete_local_node_context():
    os.remove(NODE_CONTEXT)


def get_machine_id():
    cmd = cmd_utils.Command({"_raw_params": "cat /etc/machine-id"})
    out, err = cmd.start()
    return out['stdout']


def get_node_context(etcd_client, local_node_context):
    # ensure local node context matches central store node context
    try:
        node_context = etcd_client.read('nodes/%s/Node_context/node_id' %
                                        local_node_context)
        LOG.info("Remote Node_context.node_id==%s found!" %
                 node_context.value)
        return node_context.value
    except etcd.EtcdKeyNotFound:
        # Seems like local node context is stale, delete it!
        return None
