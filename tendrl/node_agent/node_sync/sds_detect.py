import logging

import etcd

from tendrl.node_agent.discovery.sds import manager as sds_manager

LOG = logging.getLogger(__name__)


def load_and_execute_sds_discovery_plugins():
    LOG.info("load_and_execute_sds_discovery_plugins")
    try:
        sds_discovery_manager = sds_manager.SDSDiscoveryManager()
    except ValueError as ex:
        LOG.error(
            'Failed to init SDSDiscoveryManager. \Error %s', str(ex))
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
                LOG.error('Failed to update etcd . Error %s', str(ex))
            break
