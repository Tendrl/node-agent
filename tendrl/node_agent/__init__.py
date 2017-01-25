__version__ = '1.2'
try:
    from gevent import monkey
except ImportError:
    pass
else:
    monkey.patch_all()

from tendrl.commons import etcdobj
from tendrl.commons import log
from tendrl.commons import CommonNS

from tendrl.node_agent.objects.definition import Definition
from tendrl.node_agent.objects.config import Config
from tendrl.node_agent.objects.node_context import NodeContext
from tendrl.node_agent.objects.detected_cluster import DetectedCluster
from tendrl.node_agent.objects.platform import Platform
from tendrl.node_agent.objects.tendrl_context import TendrlContext
from tendrl.node_agent.objects.service import Service
from tendrl.node_agent.objects.cpu import Cpu
from tendrl.node_agent.objects.disk import Disk
from tendrl.node_agent.objects.file import File
from tendrl.node_agent.objects.memory import Memory
from tendrl.node_agent.objects.node import Node
from tendrl.node_agent.objects.os import Os
from tendrl.node_agent.objects.package import Package
from tendrl.node_agent.objects.platform import Platform

from tendrl.node_agent.flows.import_cluster import ImportCluster

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

        # etcd_orm
        etcd_kwargs = {'port': tendrl_ns.config.data['etcd_port'],
                       'host': tendrl_ns.config.data["etcd_connection"]}
        tendrl_ns.etcd_orm = etcdobj.Server(etcd_kwargs=etcd_kwargs)

        # NodeContext
        tendrl_ns.node_context = tendrl_ns.node_agent.objects.NodeContext()

        tendrl_ns.tendrl_context = tendrl_ns.node_agent.objects.TendrlContext()


        log.setup_logging(
            tendrl_ns.config.data['log_cfg_path'],
        )

import __builtin__
__builtin__.tendrl_ns = NodeAgentNS()
