from tendrl.node_agent.objects import base_object

from tendrl.node_agent.objects.definition import master


class Definition(base_object.BaseObject):
    def __init__(self, *args, **kwargs):
        super(Definition, self).__init__(*args, **kwargs)

        self.value = '_tendrl/definitions/master'
        self.master = master.data