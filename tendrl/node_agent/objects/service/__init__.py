from tendrl.commons.etcdobj import EtcdObj
from tendrl.node_agent import objects
from tendrl.commons.utils import service_status


class Service(objects.NodeAgentBaseObject):
    def __init__(self, service=None, running=None, exists=None,
                 *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        service_detail = self.get_service_info(service)
        self.value = 'nodes/%s/Services/%s'
        self.list = 'nodes/%s/Services/'
        self.running = running or service_detail['running']
        self.service = service
        self.exists = exists or service_detail['exists']
        self._etcd_cls = _ServiceEtcd

    def get_service_info(self, service_name):
        service = service_status.ServiceStatus(
            service_name,
            tendrl_ns.config.data['tendrl_ansible_exec_file']
        )
        return {"exists": service.exists(), "running": service.status()}


class _ServiceEtcd(EtcdObj):
    """A table of the service, lazily updated

    """
    __name__ = 'nodes/%s/Service/%s'
    _tendrl_cls = Service

    def render(self):
        self.__name__ = self.__name__ % (
            tendrl_ns.node_context.node_id,
            self.service
        )
        return super(_ServiceEtcd, self).render()
