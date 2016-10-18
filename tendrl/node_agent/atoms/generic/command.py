from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleRunner


ANSIBLE_MODULE_PATH = "core/commands/command.py"


class Command(object):
    def start(self, attributes):
        try:
            runner = AnsibleRunner(
                ANSIBLE_MODULE_PATH,
                **attributes
            )
            result, err = runner.run()
        except AnsibleExecutableGenerationFailed as e:
            return {}, e.message
        return result, err
