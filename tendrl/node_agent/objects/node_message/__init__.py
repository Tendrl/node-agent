
from tendrl.commons.message import Message as message
from tendrl.commons import objects


class NodeMessage(objects.BaseObject, message):
    internal = True

    def __init__(self, **node_message):
        self._defs = {}
        message.__init__(self, **node_message)
        objects.BaseObject.__init__(self)

        self.value = 'nodes/{0}/messages/{1}'

    def save(self):
        super(NodeMessage, self).save(update=False,
                                      ttl=NS.config.data[
                                          'message_retention_time'])

    def render(self):
        self.value = self.value.format(self.node_id, self.message_id)
        return super(NodeMessage, self).render()
