from tendrl.commons.message import Message as CommonMessage
from tendrl.commons import objects


class Message(objects.BaseObject, CommonMessage):
    internal = True

    def __init__(self, **message_arg):
        self._defs = {}
        CommonMessage.__init__(self, **message_arg)
        objects.BaseObject.__init__(self)
        self.value = 'messages/events/{0}'

    def save(self):
        super(Message, self).save(update=False,
                                  ttl=NS.config.data['message_retention_time'])

    def render(self):
        self.value = self.value.format(self.message_id)
        return super(Message, self).render()
