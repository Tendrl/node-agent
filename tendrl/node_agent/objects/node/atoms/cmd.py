import logging

from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleRunner


LOG = logging.getLogger(__name__)
ANSIBLE_MODULE_PATH = "core/commands/command.py"


class Cmd(object):
    def run(self, parameters):
        cmd = parameters.get("Node.cmd_str")
        try:
            runner = AnsibleRunner(
                ANSIBLE_MODULE_PATH,
                _raw_params=cmd
            )
            result, err = runner.run()
        except AnsibleExecutableGenerationFailed as ex:
            LOG.error(ex)
            return False
        LOG.info(result)
        return True
