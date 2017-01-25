from tendrl.commons import flows


class NodeAgentBaseFlow(flows.BaseFlow):
    def __init__(self, *args, **kwargs):
        super(NodeAgentBaseFlow, self).__init__(*args, **kwargs)
