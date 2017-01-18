import abc
import six


@six.add_metaclass(abc.ABCMeta)
class BaseObject(object):
    def __init__(
            self,
            name,
            attrs,
            enabled,
            obj_list,
            obj_value,
            atoms,
            flows
    ):
        self.name = name

        # list of attr tuple of (attr_name, type)
        self.attrs = attrs
        self.enabled = enabled

        # path to LIST of all instance of the object
        self.obj_list = obj_list

        # path to GET an instance of the object
        self.obj_value = obj_value
        self.atoms = atoms
        self.flows = flows
