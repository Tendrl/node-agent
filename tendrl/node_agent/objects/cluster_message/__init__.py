
from tendrl.commons.message import Message as message
from tendrl.commons import objects


class ClusterMessage(objects.BaseObject, message):
    internal = True

    def __init__(self, **cluster_message):
        self._defs = {}
        message.__init__(self, **cluster_message)
        objects.BaseObject.__init__(self)
        
        self.value = 'clusters/{0}/messages/{1}'

    def save(self):
        super(ClusterMessage, self).save(update=False,
                                         ttl=NS.config.data[
                                             'message_retention_time'])

    def render(self):
        self.value = self.value.format(self.cluster_id,
                                       self.message_id)
        return super(ClusterMessage, self).render()
