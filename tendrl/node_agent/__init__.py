try:
    from gevent import monkey
except ImportError:
    pass
else:
    monkey.patch_all()

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
from tendrl.node_agent.objects.message import Message
from tendrl.node_agent.objects.cluster_message import ClusterMessage
from tendrl.node_agent.objects.node_message import NodeMessage

from tendrl.node_agent.flows.import_cluster import ImportCluster

class NodeAgentNS(CommonNS):
    def __init__(self):

        # Create the "tendrl_ns.node_agent" namespace
        self.to_str = "tendrl.node_agent"
        self.type = 'node'
        super(NodeAgentNS, self).__init__()

NodeAgentNS()
