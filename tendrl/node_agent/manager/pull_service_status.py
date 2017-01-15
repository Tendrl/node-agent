from tendrl.commons.utils.service_status import ServiceStatus

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


def get_service_info(service_name):
    service = ServiceStatus(service_name)
    return {"exists": service.exists(), "running": service.status()}


def node_service_details():
    service_detail = {}

    for service in TENDRL_SERVICES:
        service_info = get_service_info(service)
        if service_info["exists"]:
            service_detail[service.rstrip("@*")] = service_info

    return service_detail
