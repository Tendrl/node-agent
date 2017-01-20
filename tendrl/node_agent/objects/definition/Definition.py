import namespaces as ns
import yaml

from tendrl.commons.etcdobj.etcdobj import EtcdObj
from tendrl.commons.etcdobj import fields

from tendrl.node_agent.objects import base_object
from tendrl.node_agent.objects.definition import master


# Definitions need there own special init, hence subclassing BaseObject
class Definition(base_object.BaseObject):
    def __init__(self, *args, **kwargs):
        super(Definition, self).__init__(*args, **kwargs)

        self.value = '_tendrl/definitions/master'
        self.master = master.data
        self._parsed_defs = yaml.safe_load(self.master)

    def get_obj(self, namespace, obj_name):
        raw_ns = "namespace.%s" % namespace
        raw_obj = self._parsed_defs[raw_ns]['objects'][obj_name]
        return ns.Namespace(name=obj_name, attrs=raw_obj['attrs'],
                            enabled=raw_obj['enabled'],
                            obj_list=raw_obj['list'],
                            obj_value=raw_obj['value'],
                            atoms=raw_obj.get('atoms', {}),
                            flows=raw_obj.get('flows', {}))


class _DefinitionEtcd(EtcdObj):
    """A table of the Definitions, lazily updated

    """
    __name__ = '_tendrl/definitions/master'

    def to_tendrl_obj(self):
        cls = _DefinitionEtcd
        result = Definition()
        for key in dir(cls):
            if not key.startswith('_'):
                attr = getattr(cls, key)
                if issubclass(attr.__class__, fields.Field):
                    setattr(result, key, attr.value)
        return result

# Register Tendrl object in the current namespace (Tendrl.node_agent)
Tendrl.add_object(Definition, Definition.__name__)
