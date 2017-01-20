__import__('pkg_resources').declare_namespace(__name__)
try:
    from gevent import monkey
except ImportError:
    pass
else:
    monkey.patch_all()

import namespaces as ns


class TendrlNS(object):
    def __init__(self, *args, **kwargs):
        super(TendrlNS, self).__init__()

        # Create the "Tendrl.node_agent" namespace
        self.to_str = "tendrl.node_agent"
        self.node_agent = ns.Namespace(objects=ns.Namespace(),
                                       flows=ns.Namespace())

        # Create the "Tendrl.node_agent.objects.$obj.{atoms, flows} NS
    def add_object(self, obj_class, name):
        # obj is the actual instance of that Tendrl object
        # name of object as defined in Tendrl definitions
        self.node_agent.objects[name] = obj_class

    def add_flow(self, flow_class, name):
        # flow is the actual instance of that Tendrl flow
        # name of object as defined in Tendrl definitions
        self.node_agent.flows[name] = flow_class


import __builtin__
__builtin__.Tendrl = TendrlNS()
