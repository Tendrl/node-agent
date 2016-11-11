from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleRunner


ANSIBLE_MODULE_PATH = "core/commands/command.py"


class Command(object):
    def run(self, **kwargs):
        cmd = kwargs.get("cmd_str")
        try:
            runner = AnsibleRunner(
                ANSIBLE_MODULE_PATH,
                _raw_params=cmd
            )
            result, err = runner.run()
        except AnsibleExecutableGenerationFailed:
            return {
                cmd: {
                    "result": "",
                    "rc": 1,
                    "stderr": "Ansible execution failed"
                }
            }
        return {
            cmd: {"result": result["stdout"],
                  "rc": result["rc"],
                  "stderr": result["stderr"]}
        }
