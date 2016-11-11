import logging
import os
import uuid

import time

LOG = logging.getLogger(__name__)


TENDRL_CONF_PATH = "/etc/tendrl/"
NODE_AGENT_KEY = "/etc/tendrl/node_agent_key" + str(time.time())


def configure_tendrl_uuid():
    # check if valid uuid is already present in node_agent_key
    # if not present generate one and update the file
    file_list = []
    for f in os.listdir(TENDRL_CONF_PATH):
        if f.startswith("node_agent_key_"):
            file_list.append(f)
    if len(file_list) == 0:
        with open(NODE_AGENT_KEY, 'w') as f:
            f.write(str(uuid.uuid4()))
        LOG.info("tendrl node uuid is being generated")
        return NODE_AGENT_KEY
    elif len(file_list) > 1:
        raise ValueError("detected more than one node agent key")

    try:
        with open(TENDRL_CONF_PATH + file_list[0]) as f:
            node_id = f.read()
            uuid.UUID(node_id, version=4)
            LOG.info("tendrl node uuid already exists")
            return TENDRL_CONF_PATH + file_list[0]
    except ValueError:
        os.rmdir(file_list[0])
        with open(NODE_AGENT_KEY, 'w') as f:
            f.write(str(uuid.uuid4()))
        LOG.info("tendrl node uuid is being generated")
        return None
