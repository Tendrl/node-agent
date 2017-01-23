__import__('pkg_resources').declare_namespace(__name__)
try:
    from gevent import monkey
except ImportError:
    pass
else:
    monkey.patch_all()

from tendrl.commons import etcdobj
from tendrl.commons import log
from tendrl import CommonNS

class NodeAgentNS(CommonNS):
    def __init__(self):

        # Create the "tendrl_ns.node_agent" namespace
        self.to_str = "tendrl.node_agent"
        self.type = 'node'
        super(NodeAgentNS, self).__init__()

    def setup_initial_objects(self):
        # Definitions
        tendrl_ns.definitions = tendrl_ns.node_agent.objects.Definition()

        # Config
        tendrl_ns.config = tendrl_ns.node_agent.objects.Config()

        # NodeContext
        tendrl_ns.node_context = tendrl_ns.node_agent.objects.NodeContext()

        # etcd_orm
        etcd_kwargs = {'port': tendrl_ns.config['etcd_port'],
                       'host': tendrl_ns.config["etcd_connection"]}
        tendrl_ns.etcd_orm = etcdobj.Server(etcd_kwargs=etcd_kwargs)

        log.setup_logging(
            tendrl_ns.config['log_cfg_path'],
        )


import __builtin__
__builtin__.tendrl_ns = NodeAgentNS()



