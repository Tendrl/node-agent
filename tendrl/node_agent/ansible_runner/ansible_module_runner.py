import ansible.executor.module_common as module_common
from ansible import modules
import os
import subprocess
from tendrl.node_agent.config import TendrlConfig
import uuid

config = TendrlConfig()

try:
    import json
except ImportError:
    import simplejson as json


class AnsibleExecutableGenerationFailed(Exception):
    def __init__(self, module_path=None, arguments=None, err=None):
        self.message = "Executabe could not be generated for module" \
                       " %s , with arguments %s. Error: %s" % (
                           str(module_path), str(arguments), str(err))


class AnsibleRunner(object):
    """Class that can be used to run ansible modules

    """
    def __init__(self, module_path, **kwargs):
        self.executable_module_path = config.get(
            "tendrl_node_agent",
            "tendrl_exe_file_prefix"
        ) + str(uuid.uuid4())
        self.module_path = modules.__path__[0] + "/" + module_path
        if not os.path.isfile(self.module_path):
            raise ValueError
        if kwargs == {}:
            raise ValueError
        else:
            self.argument_dict = kwargs

    def __generate_executable_module(self):
        modname = os.path.basename(self.module_path)
        modname = os.path.splitext(modname)[0]
        try:
            (module_data, module_style, shebang) = module_common.modify_module(
                modname,
                self.module_path,
                self.argument_dict,
                task_vars={}
            )
        except Exception as e:
            raise AnsibleExecutableGenerationFailed(
                self.module_path,
                self.executable_module_path,
                str(e)
            )

        with open(self.executable_module_path, 'w') as f:
            f.write(module_data)
        os.system("chmod +x %s" % self.executable_module_path)

    def __destroy_executable_module(self):
        os.remove(self.executable_module_path)

    def run(self):
        self.__generate_executable_module()

        cmd = subprocess.Popen(
            self.executable_module_path,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = cmd.communicate()
        try:
            result = json.loads(out)
        except ValueError:
            result = out

        self.__destroy_executable_module()

        return result, err
