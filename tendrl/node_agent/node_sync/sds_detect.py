import uuid

import etcd

from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.message import Message

from tendrl.node_agent.discovery.sds import manager as sds_manager


def sync():
    try:
        Event(
            Message(
                priority="debug",
                publisher=NS.publisher_id,
                payload={"message": "Running SDS detection"}
            )
        )
        try:
            sds_discovery_manager = sds_manager.SDSDiscoveryManager()
        except ValueError as ex:
            Event(
                ExceptionMessage(
                    priority="debug",
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
            if ('detected_cluster_id' in sds_details and sds_details[
                    'detected_cluster_id'] != ""):
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
                        integration_index_key = \
                            "indexes/detected_cluster_id_to_integration_id " \
                            "%s" % sds_details['detected_cluster_id']
                        try:
                            integration_id = str(uuid.uuid4())
                            NS._int.wclient.write(integration_index_key,
                                                  integration_id,
                                                  prevExist=False)
                        except etcd.EtcdAlreadyExist:
                            integration_id = NS._int.client.read(
                                integration_index_key).value
                        finally:
                            NS.tendrl_context.integration_id = integration_id
                            NS.tendrl_context.cluster_id = sds_details.get(
                                'detected_cluster_id')
                            NS.tendrl_context.cluster_name = sds_details.get(
                                'detected_cluster_name')
                            NS.tendrl_context.sds_name = sds_details.get(
                                'pkg_name')
                            NS.tendrl_context.sds_version = sds_details.get(
                                'pkg_version')
                            NS.tendrl_context.save()

                        NS.node_context = NS.node_context.load()
                        integration_tag = "tendrl/integration/%s" % \
                                          integration_id
                        detected_cluster_tag = "detected_cluster/%s" % \
                                               sds_details[
                                                   'detected_cluster_id']
                        if integration_tag in NS.node_context.tags:
                            continue
                        NS.node_context.tags += [detected_cluster_tag,
                                                 integration_tag]
                        NS.node_context.tags = list(set(NS.node_context.tags))
                        NS.node_context.save()

                    except (etcd.EtcdException, KeyError) as ex:
                        Event(
                            ExceptionMessage(
                                priority="debug",
                                publisher=NS.publisher_id,
                                payload={"message": "Failed SDS detection",
                                         "exception": ex
                                         }
                            )
                        )
                    break
    except Exception as ex:
        Event(
            ExceptionMessage(
                priority="error",
                publisher=NS.publisher_id,
                payload={"message": "node_sync "
                                    "SDS detection failed: " +
                                    ex.message,
                         "exception": ex}
            )
        )
