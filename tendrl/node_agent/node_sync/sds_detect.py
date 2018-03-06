import time
import uuid

import etcd

from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.objects.job import Job
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger
from tendrl.node_agent.discovery.sds import manager as sds_manager


def sync(sync_ttl):
    try:
        logger.log(
            "debug",
            NS.publisher_id,
            {"message": "Running SDS detection"}
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
            if sds_details is None:
                break
            if ('detected_cluster_id' in sds_details and sds_details[
                    'detected_cluster_id'] != ""):
                try:
                    integration_index_key = \
                        "indexes/detected_cluster_id_to_integration_id/" \
                        "%s" % sds_details['detected_cluster_id']
                    dc = NS.tendrl.objects.DetectedCluster().load()
                    if dc is None or dc.detected_cluster_id is None:
                        time.sleep(sync_ttl)
                        integration_id = str(uuid.uuid4())
                        try:
                            NS._int.wclient.write(
                                integration_index_key,
                                integration_id,
                                prevExist=False
                            )
                        except etcd.EtcdAlreadyExist:
                            pass
                    
                    _ptag = None
                    if NS.tendrl_context.integration_id:
                        _ptag = "provisioner/%s" % \
                            NS.tendrl_context.integration_id
                        
                        _target = "tendrl/node_%s" % \
                            NS.node_context.node_id
                        _flow = "tendrl.flows." \
                            "ExpandClusterWithDetectedPeers"

                        if _ptag in NS.node_context.tags:
                            if dc.detected_cluster_id and \
                                dc.detected_cluster_id != sds_details.get(
                                    'detected_cluster_id'):
                                
                                # Gluster peer list has changed
                                integration_id = \
                                    NS.tendrl_context.integration_id
                                etcd_utils.write(
                                    integration_index_key,
                                    integration_id
                                )
                                # Let other nodes sync up with
                                # integration_id
                                params = {
                                    'TendrlContext.integration_id':
                                    integration_id,
                                }
                                payload = {
                                    "tags": [_target],
                                    "run": _flow,
                                    "status": "new",
                                    "parameters": params,
                                    "type": "node"
                                }
                                _job_id = str(uuid.uuid4())
                                _job = Job(
                                    job_id=_job_id,
                                    status="new",
                                    payload=payload,
                                    timeout="no"
                                ).save()
                                while True:
                                    _job = _job.load()
                                    if _job.status in ["finished",
                                                       "failed"]:
                                        break

                    loop_count = 0
                    while True:
                        # Wait till provisioner node assigns
                        # integration_id for this detected_cluster_id
                        if loop_count >= 72:
                            return
                        try:
                            time.sleep(5)
                            integration_id = etcd_utils.read(
                                integration_index_key).value
                            if integration_id:
                                break
                        except etcd.EtcdKeyNotFound:
                            loop_count += 1
                            continue

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
                    NS.node_context.tags += [detected_cluster_tag,
                                             integration_tag]
                    NS.node_context.tags = list(set(NS.node_context.tags))
                    NS.node_context.save()

                    NS.tendrl.objects.DetectedCluster(
                        detected_cluster_id=sds_details.get(
                            'detected_cluster_id'),
                        detected_cluster_name=sds_details.get(
                            'detected_cluster_name'),
                        sds_pkg_name=sds_details.get('pkg_name'),
                        sds_pkg_version=sds_details.get('pkg_version'),
                    ).save()
                    _cluster = NS.tendrl.objects.Cluster(
                        integration_id=NS.tendrl_context.integration_id
                    ).load()
                    _cluster.save()

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
