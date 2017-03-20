try:
    from gevent import monkey
except ImportError:
    pass
else:
    monkey.patch_all()

from tendrl.commons import TendrlNS


class NodeAgentNS(TendrlNS):
    def __init__(self, ns_name="node_agent",
                 ns_src="tendrl.node_agent"):
        super(NodeAgentNS, self).__init__(ns_name, ns_src)
