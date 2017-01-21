__import__('pkg_resources').declare_namespace(__name__)
try:
    from gevent import monkey
except ImportError:
    pass
else:
    monkey.patch_all()

import namespaces as ns


class TendrlNS(object):
    def __init__(self):
        super(TendrlNS, self).__init__()

        # Create the "tendrl_ns.node_agent" namespace
        self.to_str = "tendrl.node_agent"
        self.node_agent = ns.Namespace(objects=ns.Namespace(),
                                       flows=ns.Namespace())

        # Create the "tendrl_ns.node_agent.objects.$obj.{atoms, flows} NS
    def add_object(self, name, obj_class):
        # obj is the actual instance of that Tendrl object
        # name of object as defined in Tendrl definitions
        self.node_agent.objects[name] = obj_class

        # This is to link atoms and flows (insdie obj) to the obj ns
        private_name = "_" + name
        self.node_agent.objects[private_name] = ns.Namespace()

        if 'atoms' not in self.node_agent.objects[private_name]:
            self.node_agent.objects[private_name]['atoms'] = ns.Namespace()

        if "flows" not in self.node_agent.objects[private_name]:
            self.node_agent.objects[private_name]['flows'] = ns.Namespace()

    def get_object(self, name):
        return self.node_agent.objects[name]

    def get_atom(self, obj_name, atom_name):
        private_name = "_" + obj_name
        return self.node_agent.objects[private_name]['atoms'][atom_name]

    def get_obj_flow(self, obj_name, flow_name):
        private_name = "_" + obj_name
        return self.node_agent.objects[private_name]['flows'][flow_name]


    def add_atom(self, obj_name, atom_name, atom_class):
        private_name = "_" + obj_name
        self.node_agent.objects[private_name]['atoms'][atom_name] = atom_class

    def add_obj_flow(self, obj_name, flow_name, flow_class):
        private_name = "_" + obj_name
        self.node_agent.objects[private_name]['flows'][flow_name] = flow_class

    def add_flow(self, name, flow_class):
        # flow is the actual instance of that Tendrl flow
        # name of object as defined in Tendrl definitions
        self.node_agent.flows[name] = flow_class

    def get_flow(self, name):
        return self.node_agent.flows[name]


import __builtin__
__builtin__.tendrl_ns = TendrlNS()



# Discover/Register objects
from tendrl.node_agent.objects.definition import Definition

tendrl_ns.add_object(Definition.__name__, Definition)

