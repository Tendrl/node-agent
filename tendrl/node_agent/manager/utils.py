import logging
import os
import os.path
import uuid

LOG = logging.getLogger(__name__)
NODE_CONTEXT = "/etc/tendrl/node_agent/node_context"


def get_tendrl_uuid():
    # check if valid uuid is already present in node_context
    # if not present generate one and update the file
    if os.path.isfile(NODE_CONTEXT):
        with open(NODE_CONTEXT) as f:
            node_id = f.read()
            LOG.info("Tendrl Node.id==%s found!" % node_id)
            return node_id
    else:
        with open(NODE_CONTEXT, 'wb+') as f:
            node_id = str(uuid.uuid4())
            f.write(node_id)
            LOG.info("Tendrl Node.id==%s created!" % node_id)
            return node_id

