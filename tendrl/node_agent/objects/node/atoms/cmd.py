import subprocess

from tendrl.commons.atoms import base_atom


class Cmd(base_atom.BaseAtom):
    def run(self, parameters):
        cmd = parameters.get("Node.cmd_str")
        cmd = ["nohup"] + cmd.split(" ")
        subprocess.Popen(cmd)
        return True
