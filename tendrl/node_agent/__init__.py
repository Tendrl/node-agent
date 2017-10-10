from tendrl.commons import TendrlNS
from tendrl.node_agent import log


class NodeAgentNS(TendrlNS):
    def __init__(self, ns_name="node_agent",
                 ns_src="tendrl.node_agent"):
        super(NodeAgentNS, self).__init__(ns_name, ns_src)

        log.setup_logging(self.current_ns.config.data['log_cfg_path'])
