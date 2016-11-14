import logging

from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleRunner


LOG = logging.getLogger(__name__)
ANSIBLE_MODULE_PATH = "core/commands/command.py"


class Cmd(object):
    def run(self, paramaeters):
        cmd = paramaeters.get("cmd_str")
        try:
            runner = AnsibleRunner(
                ANSIBLE_MODULE_PATH,
                _raw_params=cmd
            )
            result, err = runner.run()
        except AnsibleExecutableGenerationFailed as ex:
            #{
            #    cmd: {
            #        "result": "",
            #        "rc": 1,
            #        "stderr": "Ansible execution failed"
            #    }

            LOG.error(ex)
            return False
 #       return {
 #           cmd: {"result": result["stdout"],
 #                 "rc": result["rc"],
 #                 "stderr": result["stderr"]}
 #       }
        LOG.info(result['stdout'])
        LOG.error(result.get("stderr"))
        return True
