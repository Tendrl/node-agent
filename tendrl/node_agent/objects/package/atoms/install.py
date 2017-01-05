from tendrl.common.atoms.base_atom import BaseAtom
from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.node_agent.ansible_runner.ansible_module_runner \
    import AnsibleRunner


class Install(BaseAtom):
    def run(self, parameters):
        name = parameters.get("Package.name")
        package_type = parameters.get("Package.pkg_type", "pip")
        version = parameters.get("Package.version", None)
        attributes = {}
        attributes["name"] = name
        if version:
            attributes["version"] = version

        if package_type == "pip":
            attributes["editable"] = "false"
            ansible_module_path = "core/packaging/language/pip.py"
        elif package_type == "rpm":
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
            parameters.update({"Package.state": "uninstalled"})
            return False
        parameters.update({"Package.state": "installed"})
        return True
