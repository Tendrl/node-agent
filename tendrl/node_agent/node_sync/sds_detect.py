import etcd

from tendrl.commons.event import Event
from tendrl.commons.message import Message, ExceptionMessage

from tendrl.node_agent.discovery.sds import manager as sds_manager


def load_and_execute_sds_discovery_plugins():
    Event(
        Message(
            priority="info",
            publisher=NS.publisher_id,
            payload={"message": "load_and_execute_sds_discovery_plugins"}
        )
    )
    try:
        sds_discovery_manager = sds_manager.SDSDiscoveryManager()
    except ValueError as ex:
        Event(
            ExceptionMessage(
                priority="error",
                publisher=NS.publisher_id,
                payload={"message": "Failed to init SDSDiscoveryManager.",
                         "exception": ex
                }
            )
        )
        return

    # Execute the SDS discovery plugins and tag the nodes with data
    for plugin in sds_discovery_manager.get_available_plugins():
        sds_details = plugin.discover_storage_system()
        if sds_details:
            try:
                NS.tendrl.objects.DetectedCluster(
                    detected_cluster_id=sds_details.get(
                        'detected_cluster_id'),
                    sds_pkg_name=sds_details.get('pkg_name'),
                    sds_pkg_version=sds_details.get('pkg_version'),
                ).save()
            except etcd.EtcdException as ex:
                Event(
                    ExceptionMessage(
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={"message": "Failed to update etcd .",
                                 "exception": ex
                                 }
                    )
                )
            break
