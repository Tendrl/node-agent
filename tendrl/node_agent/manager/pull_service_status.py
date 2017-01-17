from tendrl.commons.config import load_config
from tendrl.commons.utils import service_status

TENDRL_SERVICE_TAGS = {
    "tendrl-node-agent": "TENDRL",
    "etcd": "TENDRL_SERVER",
    "tendrl-apid": "TENDRL_SERVER",
    "tendrl-gluster-integration": "TENDRL_GLUSTER",
    "tendrl-ceph-integration": "TENDRL_CEPH",
    "glusterd": "GLUSTER",
    "ceph-mon": "CEPH_MON",
    "ceph-osd": "CEPH_OSD"
}

TENDRL_SERVICES = [
    "tendrl-node-agent",
    "etcd",
    "tendrl-apid",
    "tendrl-gluster-integration",
    "tendrl-ceph-integration",
    "glusterd",
    "ceph-mon@*",
    "ceph-osd@*",

]

config = load_config("node-agent",
                     "/etc/tendrl/node-agent/node-agent.conf.yaml")

def get_service_info(service_name):
    service = service_status.ServiceStatus(service_name,
                                           config['tendrl_ansible_exec_file'])
    return {"exists": service.exists(), "running": service.status()}


def node_service_details():
    service_detail = {}

    for service in TENDRL_SERVICES:
        service_info = get_service_info(service)
        if service_info["exists"]:
            service_detail[service.rstrip("@*")] = service_info

    return service_detail
