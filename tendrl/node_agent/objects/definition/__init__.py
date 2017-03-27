import pkg_resources
from ruamel import yaml
from tendrl.commons import etcdobj
from tendrl.commons import objects

# Definitions need there own special init and have to be present in the NS
# before anything else, Hence subclassing BaseObject


class Definition(objects.BaseObject):
    internal = True
    def __init__(self, *args, **kwargs):
        super(Definition, self).__init__(*args, **kwargs)

        self.value = '_NS/node_agent/definitions'
        self.data = pkg_resources.resource_string(__name__, "node_agent.yaml")
        self._parsed_defs = yaml.safe_load(self.data)
        self._etcd_cls = _DefinitionEtcd
        self._defs = {}

    def get_parsed_defs(self):
        self._parsed_defs = yaml.safe_load(self.data)
        return self._parsed_defs

class _DefinitionEtcd(etcdobj.EtcdObj):
    """A table of the Definitions, lazily updated

    """
    __name__ = '_NS/node_agent/definitions'
    _tendrl_cls = Definition
