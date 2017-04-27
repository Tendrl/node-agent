import etcd
import json

from tendrl.commons.event import Event
from tendrl.commons.message import Message, ExceptionMessage

from tendrl.node_agent.discovery.sds import manager as sds_manager


def load_and_execute_sds_discovery_plugins():
    Event(
        Message(
            priority="debug",
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
        if 'detected_cluster_id' in sds_details:
            if sds_details:
                try:
                    NS.tendrl.objects.DetectedCluster(
                        detected_cluster_id=sds_details.get(
                            'detected_cluster_id'),
                        detected_cluster_name=sds_details.get(
                            'detected_cluster_name'),
                        sds_pkg_name=sds_details.get('pkg_name'),
                        sds_pkg_version=sds_details.get('pkg_version'),
                    ).save()
                    NS.node_context = NS.node_context.load()
                    current_tags = json.loads(NS.node_context.tags)
                    detected_cluster_tag = "detected_cluster/%s" % sds_details['detected_cluster_id']
                    current_tags += [detected_cluster_tag]
                    NS.node_context.tags = list(set(current_tags))
                    NS.node_context.save()

                except (etcd.EtcdException, KeyError) as ex:
                    Event(
                        ExceptionMessage(
                            priority="error",
                            publisher=NS.publisher_id,
                            payload={"message": "Failed to update sds_discovery",
                                     "exception": ex
                                     }
                        )
                    )
                break
