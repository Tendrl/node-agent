try:
    from gevent import monkey
except ImportError:
    pass
else:
    monkey.patch_all()

from tendrl.commons import CommonNS


class NodeAgentNS(CommonNS):
    def __init__(self):

        # Create the "tendrl_ns.node_agent" namespace
        self.to_str = "tendrl.node_agent"
        self.type = 'node'
        super(NodeAgentNS, self).__init__()

NodeAgentNS()
