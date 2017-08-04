#! /usr/bin/env python

import json
import os
import platform
import socket
from sys import argv


from jinja2 import Environment
from jinja2 import FileSystemLoader


collectd_os_specifics = {
    'Fedora': {
        'config': '/etc/collectd.conf',
        'moduledirconfig': '/usr/lib64/collectd/',
        'pluginconf': '/etc/collectd.d',
        'socketgroup': 'wheel',
    },
    'centos': {
        'config': '/etc/collectd.conf',
        'pluginconf': '/etc/collectd.d',
        'moduledirconfig': '/usr/lib64/collectd/',
        'socketgroup': 'wheel',
    },
    'redhat': {
        'config': '/etc/collectd.conf',
        'pluginconf': '/etc/collectd.d',
        'moduledirconfig': '/usr/lib64/collectd/',
        'socketgroup': 'wheel',
    },
}[platform.dist()[0]]

TEMPLATE_ROOT = '/etc/collectd_template'


class TendrlMonitoringConfigManager(object):

    def __init__(self, conf_name, data):
        self.template_path = '%s/%s.jinja' % (TEMPLATE_ROOT, conf_name)
        if conf_name == 'collectd':
            self.config_path = collectd_os_specifics['config']
        else:
            self.config_path = '%s/%s.conf' % (
                collectd_os_specifics['pluginconf'], conf_name)
        self.data = data
        self.data.update(collectd_os_specifics)
        self.data['hostname'] = socket.getfqdn()

    def generate_config_file(self):
        j2_env = Environment(
            loader=FileSystemLoader(
                os.path.dirname(self.template_path)
            )
        )
        template = j2_env.get_template(os.path.basename(self.template_path))
        conf_str = template.render(self.data)
        text_file = open(self.config_path, "w")
        text_file.write("%s\n" % conf_str)
        text_file.close()


def main():
    conf_name = argv[1]
    data = json.loads(argv[2])
    TendrlMonitoringConfigManager(conf_name, data).generate_config_file()
    return 0


if __name__ == '__main__':
    main()
