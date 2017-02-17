import os

from tendrl.node_agent import objects
from tendrl.node_agent.objects import node


class CheckNodeUp(objects.NodeAgentBaseAtom):
    obj = node.Node

    def run(self):
        fqdn = self.parameters.get("fqdn")
        response = os.system("ping -c 1 " + fqdn)
        # and then check the response...
        if response == 0:
            return True
        else:
            return False
