import logging
import os
import os.path
import uuid

LOG = logging.getLogger(__name__)
NODE_CONTEXT = "/etc/tendrl/node_agent/node_context"


def get_node_context():
    # check if valid uuid is already present in node_context
    # if not present generate one and update the file
    if os.path.isfile(NODE_CONTEXT):
        with open(NODE_CONTEXT) as f:
            node_id = f.read()
            if node_id:
                LOG.info("Node_context.node_id==%s found!" % node_id)
                return node_id
    else:
        return None


def set_node_context():
    node_id = get_node_context()
    if node_id is None:
        with open(NODE_CONTEXT, 'wb+') as f:
            node_id = str(uuid.uuid4())
            f.write(node_id)
            LOG.info("Node_context.node_id==%s created!" % node_id)

    return node_id
