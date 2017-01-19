import logging
import os
import os.path
import uuid

import etcd

from tendrl.commons.config import load_config

LOG = logging.getLogger(__name__)
NODE_CONTEXT = "/etc/tendrl/node-agent/node_context"
config = load_config("node-agent",
                     "/etc/tendrl/node-agent/node-agent.conf.yaml")


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


def get_node_context(etcd_orm, local_node_context):
    # ensure local node context matches central store node context
    try:
        node_context = etcd_orm.client.read('nodes/%s/Node_context/node_id' %
                                            local_node_context)
        LOG.info("Remote Node_context.node_id==%s found!" %
                 node_context.value)
        return node_context.value
    except etcd.EtcdKeyNotFound:
        # Seems like local node context is stale, delete it!
        return None
