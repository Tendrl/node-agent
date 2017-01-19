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

    def __new__(cls, *args, **kwargs):
        # Register Tendrl object in the current namespace (Tendrl.node_agent)
        Tendrl.add_object(cls, cls.__name__)

        super_new = super(BaseObject, cls).__new__
        if super_new is object.__new__:
            instance = super_new(cls)
        else:
            instance = super_new(cls, *args, **kwargs)

        return instance