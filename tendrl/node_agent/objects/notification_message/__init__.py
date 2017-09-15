from tendrl.commons.message import Message as CommonMessage
from tendrl.commons import objects


class NotificationMessage(objects.BaseObject, CommonMessage):
    internal = True

    def __init__(self, **notification_message):
        self._defs = {}
        CommonMessage.__init__(self, **notification_message)
        objects.BaseObject.__init__(self)

        self.value = '_tendrl/notifications/{0}'

    def save(self):
        super(NotificationMessage, self).save(
            update=False,
            ttl=NS.config.data['message_retention_time']
        )

    def render(self):
        self.value = self.value.format(self.message_id)
        return super(NotificationMessage, self).render()
