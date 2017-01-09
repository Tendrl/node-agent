import subprocess

from tendrl.commons.atoms.base_atom import BaseAtom


class Cmd(BaseAtom):
    def run(self, parameters):
        cmd = parameters.get("Node.cmd_str")
        cmd = ["nohup"] + cmd.split(" ")
        subprocess.Popen(cmd)
        return True
