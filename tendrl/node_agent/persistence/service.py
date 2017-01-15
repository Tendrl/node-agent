from tendrl.commons.etcdobj.etcdobj import EtcdObj
from tendrl.commons.etcdobj import fields


class Service(EtcdObj):
    """A table of the service, lazily updated

    """
    __name__ = 'nodes/%s/Services/%s'

    node_id = fields.StrField("node_id")
    exists = fields.StrField("exists")
    running = fields.StrField("running")
    service = fields.StrField("service")

    def render(self):
        self.__name__ = self.__name__ % (self.node_id, self.service)
        return super(Service, self).render()
