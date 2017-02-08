# flake8: noqa

import subprocess

from tendrl.commons.utils import ansible_module_runner
import yaml


def import_gluster(integration_id):
    attributes = {}
    if tendrl_ns.config.data['package_source_type'] == 'pip':
        name = "git+https://github.com/Tendrl/gluster-integration.git@v1.2"
        attributes["name"] = name
        attributes["editable"] = "false"
        ansible_module_path = "core/packaging/language/pip.py"
    elif tendrl_ns.config.data['package_source_type'] == 'rpm':
        name = "tendrl-gluster-integration"
        ansible_module_path = "core/packaging/os/yum.py"
        attributes["name"] = name
    else:
        return False

    try:
        runner = ansible_module_runner.AnsibleRunner(
            ansible_module_path,
            tendrl_ns.config.data['tendrl_ansible_exec_file'],
            **attributes
        )
        result, err = runner.run()
    except ansible_module_runner.AnsibleExecutableGenerationFailed:
        return False
    
    with open("/etc/tendrl/gluster-integration/gluster-integration_logging"
                       ".yaml", 'w+') as f:
        f.write(logging_file)

    config_data = {"etcd_port": tendrl_ns.config.data['etcd_port'],
                   "etcd_connection": tendrl_ns.config.data['etcd_connection'],
                   "tendrl_ansible_exec_file": "$HOME/.tendrl/gluster-integration/ansible_exec",
                   "log_cfg_path":"/etc/tendrl/gluster-integration/gluster-integration_logging"
                       ".yaml", "log_level": "DEBUG"}
    with open("/etc/tendrl/gluster-integration/gluster-integration"
              ".conf.yaml", 'w') as outfile:
        yaml.dump(config_data, outfile, default_flow_style=False)

    gluster_integration_context = "/etc/tendrl/gluster-integration/integration_id"
    with open(gluster_integration_context, 'wb+') as f:
        f.write(integration_id)

    subprocess.Popen(["nohup", "tendrl-gluster-integration", "&"])










logging_file = """version: 1
disable_existing_loggers: False
formatters:
    simple:
        format: "%(asctime)s - %(pathname)s - %(filename)s:%(lineno)s - %(funcName)20s() - %(levelname)s - %(message)s"
        datefmt: "%Y-%m-%dT%H:%M:%S%z"

handlers:
    console:
        class: logging.StreamHandler
        level: DEBUG
        formatter: simple
        stream: ext://sys.stdout

    info_file_handler:
        class: logging.handlers.TimedRotatingFileHandler
        level: INFO
        formatter: simple
        filename: /var/log/tendrl/gluster-integration/gluster-integration_info.log

    error_file_handler:
        class: logging.handlers.RotatingFileHandler
        level: ERROR
        formatter: simple
        filename: /var/log/tendrl/gluster-integration/gluster-integration_errors.log
        maxBytes: 10485760 # 10MB
        backupCount: 20
        encoding: utf8

loggers:
    my_module:
        level: ERROR
        handlers: [console]
        propagate: no

root:
    level: INFO
    handlers: [console, info_file_handler, error_file_handler]
"""
