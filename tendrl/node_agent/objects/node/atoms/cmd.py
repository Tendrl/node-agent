import subprocess

from tendrl.node_agent import objects
from tendrl.node_agent.objects import node


class Cmd(objects.NodeAgentBaseAtom):
    obj = node.Node

    def run(self):
        cmd = self.parameters.get("Node.cmd_str")
        cmd = ["nohup"] + cmd.split(" ")
        subprocess.Popen(cmd)
        return True
