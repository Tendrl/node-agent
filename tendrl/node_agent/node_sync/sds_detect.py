import etcd
import json
import socket
import subprocess
import time
import uuid


from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import event_utils
from tendrl.commons.utils import log_utils as logger
from tendrl.node_agent.discovery.sds import manager as sds_manager


def sync(sync_ttl):
    try:
        NS.node_context = NS.node_context.load()
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

            if "peers" in sds_details and NS.tendrl_context.integration_id:
                _cnc = NS.tendrl.objects.ClusterNodeContext().load()
                this_peer_uuid = ""
                if _cnc.is_managed != "yes" or not NS.node_context.fqdn:
                    for peer_uuid, data in sds_details.get("peers",
                                                           {}).iteritems():
                        peer = NS.tendrl.objects.GlusterPeer(
                            peer_uuid=peer_uuid,
                            hostname=data['hostname'],
                            connected=data['connected']
                        )
                        peer.save()
                        if data['hostname'] == "localhost":
                            this_peer_uuid = peer_uuid

                    # Figure out the hostname used to probe this peer
                    integration_id_index_key = \
                        "indexes/tags/tendrl/integration/%s" %\
                        NS.tendrl_context.integration_id
                    _node_ids = etcd_utils.read(integration_id_index_key).value
                    _node_ids = json.loads(_node_ids)
                    if len(_node_ids) == 1:
                        NS.node_context.fqdn = socket.getfqdn()
                        NS.node_context.pkey = NS.node_context.fqdn
                        NS.node_context.ipv4_addr = socket.gethostbyname(
                            NS.node_context.fqdn
                        )
                        NS.node_context.save()
                    peer_node_id = ""
                    for _node_id in _node_ids:
                        if _node_id != NS.node_context.node_id:
                            peer_node_id = _node_id
                            break

                    if peer_node_id:
                        peer = NS.tendrl.objects.GlusterPeer(
                            peer_uuid=this_peer_uuid, node_id=peer_node_id
                        ).load()
                        NS.node_context.pkey = peer.hostname
                        NS.node_context.fqdn = peer.hostname
                        NS.node_context.ipv4_addr = socket.gethostbyname(
                            peer.hostname
                        )
                        NS.node_context.save()

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
                            etcd_utils.write(
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
                                # Raise an alert regarding the same
                                msg = "New peers identified in cluster: %s. " \
                                    "Make sure tendrl-ansible is executed " \
                                    "for the new nodes so that expand " \
                                    "cluster option can be triggered" % \
                                    integration_id
                                event_utils.emit_event(
                                    "cluster_status",
                                    "new_peers_detected",
                                    msg,
                                    "cluster_{0}".format(integration_id),
                                    "WARNING",
                                    integration_id=integration_id
                                )
                                # Set the cluster status as new peer detected
                                _cluster = NS.tendrl.objects.Cluster(
                                    integration_id=integration_id
                                ).load()
                                _cluster.status = "new_peers_detected"
                                _cluster.save()
                            _cluster = NS.tendrl.objects.Cluster(
                                integration_id=NS.tendrl_context.integration_id
                            ).load()
                            if _cluster.status == "new_peers_detected":
                                peers = []
                                cmd = subprocess.Popen(
                                    "gluster pool list",
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE
                                )
                                out, err = cmd.communicate()
                                if err or out is None or \
                                    "Connection failed" in out:
                                    pass  # set the no of peers as zero
                                if out:
                                    lines = out.split('\n')[1:]
                                    for line in lines:
                                        if line.strip() != '':
                                            peers.append(line.split()[0])
                                nodes_ids = json.loads(etcd_utils.read(
                                    "indexes/tags/tendrl/integration/%s" %
                                    NS.tendrl_context.integration_id
                                ).value)
                                if len(nodes_ids) == len(peers):
                                    # All the nodes are having node-agents
                                    # running and known to tendrl
                                    msg = "New nodes in cluster: %s have " \
                                        "node agents running now. Cluster " \
                                        "is ready to expand." % \
                                        NS.tendrl_context.integration_id
                                    event_utils.emit_event(
                                        "cluster_status",
                                        "expand_pending",
                                        msg,
                                        "cluster_{0}".format(
                                            NS.tendrl_context.integration_id
                                        ),
                                        "INFO",
                                        integration_id=NS.tendrl_context.
                                        integration_id
                                    )
                                    # Set the cluster status accordingly
                                    _cluster.status = 'expand_pending'
                                    _cluster.save()
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
                    if _cluster.current_job.get(
                        'status', ''
                    ) in ['', 'finished', 'failed'] \
                        and _cluster.status in [None, ""]:
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
