
from tendrl.commons.message import Message as CommonMessage
from tendrl.commons import objects


class ClusterMessage(objects.BaseObject, CommonMessage):
    internal = True

    def __init__(self, **cluster_message):
        self._defs = {}
        CommonMessage.__init__(self, **cluster_message)
        objects.BaseObject.__init__(self)
        self.value = 'clusters/{0}/messages/{1}'

    def save(self):
        super(ClusterMessage, self).save(update=False,
                                         ttl=NS.config.data[
                                             'message_retention_time'])

    def render(self):
        self.value = self.value.format(self.integration_id,
                                       self.message_id)
        return super(ClusterMessage, self).render()
