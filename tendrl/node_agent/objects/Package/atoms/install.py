from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleRunner


class Install(object):
    def run(self, **kwargs):
        name = kwargs.get("name")
        package_type = kwargs.get("pkg_type")
        version = kwargs.get("version", default=None)
        attributes = {}
        attributes["name"] = name
        if version:
            attributes["version"] = version

        if package_type == "pip":
            attributes["editable"] = "false"
            ansible_module_path = "core/packaging/language/pip.py"
        elif package_type == "yum":
            ansible_module_path = "core/packaging/os/yum.py"
        elif package_type == "deb":
            ansible_module_path = "core/packaging/os/apt.py"

        try:
            runner = AnsibleRunner(
                ansible_module_path,
                **attributes
            )
            result, err = runner.run()
        except AnsibleExecutableGenerationFailed:
            return {name: False}
        return {name: True}
