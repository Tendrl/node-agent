from ruamel import yaml
from tendrl.commons import etcdobj
from tendrl.commons import objects
from tendrl.integrations.gluster.objects.definition import definitions

# Definitions need there own special init and have to be present in the NS
# before anything else, Hence subclassing BaseObject


class Definition(objects.BaseObject):
    def __init__(self, *args, **kwargs):
        super(Definition, self).__init__(*args, **kwargs)

        self.value = '_tendrl/integrations/gluster/definitions'
        self.data = definitions.data
        self._parsed_defs = yaml.safe_load(self.data)
        self._etcd_cls = _DefinitionEtcd

    def get_parsed_defs(self):
        self._parsed_defs = yaml.safe_load(self.data)
        return self._parsed_defs

    def load_definition(self):
        return {}


class _DefinitionEtcd(etcdobj.EtcdObj):
    """A table of the Definitions, lazily updated

    """
    __name__ = '_tendrl/integrations/gluster/definitions'
    _tendrl_cls = Definition
