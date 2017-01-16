from tendrl.commons.atoms.base_atom import BaseAtom
from tendrl.commons.utils import ansible_module_runner


class Install(BaseAtom):
    def run(self):
        name = self.parameters.get("Package.name")
        package_type = self.parameters.get("Package.pkg_type", "pip")
        version = self.parameters.get("Package.version", None)
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
            runner = ansible_module_runner.AnsibleRunner(
                ansible_module_path,
                self.config['tendrl_ansible_exec_file']
                **attributes
            )
            result, err = runner.run()
        except ansible_module_runner.AnsibleExecutableGenerationFailed:
            self.parameters.update({"Package.state": "uninstalled"})
            return False
        self.parameters.update({"Package.state": "installed"})
        return True
