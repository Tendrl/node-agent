import logging

from tendrl.commons import flows

LOG = logging.getLogger(__name__)


class NodeAgentBaseFlow(flows.BaseFlow):
    def __init__(self, *args, **kwargs):
        super(NodeAgentBaseFlow, self).__init__(*args, **kwargs)
