__import__('pkg_resources').declare_namespace(__name__)
try:
    from gevent import monkey
except ImportError:
    pass
else:
    monkey.patch_all()

import namespaces as ns

class Tendrl(object):
    def __init__(self, *args, **kwargs):
        super(Tendrl, self).__init__()
        self.node_agent = ns.Namespace(objects=ns.Namespace(),
                                       flows=ns.Namespace())

    def add_object(self, obj, name):
        # obj is the actual instance of that Tendrl object
        # name of object as defined in Tendrl definitions
        self.node_agent.objects[name] = obj

    def add_flow(self, flow, name):
        # flow is the actual instance of that Tendrl flow
        # name of object as defined in Tendrl definitions
        self.node_agent.flows[name] = flow


import __builtin__
__builtin__.Tendrl = Tendrl()
