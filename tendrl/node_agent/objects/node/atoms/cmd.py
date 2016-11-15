import logging
import subprocess

LOG = logging.getLogger(__name__)

class Cmd(object):
    def run(self, parameters):
        cmd = parameters.get("Node.cmd_str")
        cmd = ["nohup"] + cmd.split(" ")
        subprocess.Popen(cmd)
        return True