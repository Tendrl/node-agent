import threading
import time

from etcd import EtcdException

from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons import sds_sync
from tendrl.commons.utils import log_utils as logger
from tendrl.commons.utils import time_utils

from tendrl.integrations.gluster import check_cluster_status


from tendrl.node_agent.node_sync import check_all_managed_nodes_status
from tendrl.node_agent.node_sync import cluster_contexts_sync
from tendrl.node_agent.node_sync import disk_sync
from tendrl.node_agent.node_sync import network_sync
from tendrl.node_agent.node_sync import platform_detect
from tendrl.node_agent.node_sync import sds_detect
from tendrl.node_agent.node_sync import services_and_index_sync


class NodeAgentSyncThread(sds_sync.StateSyncThread):
    def run(self):
        logger.log(
            "info",
            NS.publisher_id,
            {"message": "%s running" % self.__class__.__name__}
        )
        NS.node_context = NS.node_context.load()
        current_tags = list(NS.node_context.tags)
        current_tags += ["tendrl/node_%s" % NS.node_context.node_id]
        NS.node_context.tags = list(set(current_tags))
        NS.node_context.status = "UP"
        NS.node_context.save()
        _sleep = 0
        while not self._complete.is_set():
            _sync_ttl = int(NS.config.data.get("sync_interval", 10)) + 100
            if _sleep > 5:
                _sleep = int(NS.config.data.get("sync_interval", 10))
            else:
                _sleep += 1

            NS.node_context = NS.node_context.load()
            NS.node_context.sync_status = "in_progress"

            current_tags = list(NS.node_context.tags)
            current_tags += ["tendrl/node_%s" % NS.node_context.node_id]
            NS.node_context.tags = list(set(current_tags))
            NS.node_context.status = "UP"
            NS.node_context.save(ttl=_sync_ttl)
            NS.tendrl_context = NS.tendrl_context.load()

            sync_service_and_index_thread = threading.Thread(
                target=services_and_index_sync.sync, args=(_sync_ttl,))
            sync_service_and_index_thread.daemon = True
            sync_service_and_index_thread.start()
            sync_service_and_index_thread.join()

            NS.node_context = NS.node_context.load()
            if "tendrl/monitor" in NS.node_context.tags:
                check_all_managed_node_status_thread = threading.Thread(
                    target=check_all_managed_nodes_status.run)
                check_all_managed_node_status_thread.daemon = True
                check_all_managed_node_status_thread.start()
                check_all_managed_node_status_thread.join()

                check_cluster_status_thread = threading.Thread(
                    target=check_cluster_status.run
                )
                check_cluster_status_thread.daemon = True
                check_cluster_status_thread.start()
                check_cluster_status_thread.join()

            if "tendrl/monitor" not in NS.node_context.tags:
                sync_cluster_contexts_thread = threading.Thread(
                    target=cluster_contexts_sync.sync,
                    args=(_sync_ttl,)
                )
                sync_cluster_contexts_thread.daemon = True
                sync_cluster_contexts_thread.start()
                sync_cluster_contexts_thread.join()

            platform_detect_thread = threading.Thread(
                target=platform_detect.sync)
            platform_detect.daemon = True
            platform_detect_thread.start()
            platform_detect_thread.join()

            if "tendrl/monitor" not in NS.node_context.tags:
                sds_detect_thread = threading.Thread(
                    target=sds_detect.sync,
                    args=(_sleep, _sync_ttl,)
                )

                sds_detect_thread.daemon = True
                sds_detect_thread.start()
                sds_detect_thread.join()

            NS.tendrl_context = NS.tendrl_context.load()

            try:
                NS.tendrl.objects.Os().save()
                NS.tendrl.objects.Cpu().save()
                NS.tendrl.objects.Memory().save()
            except Exception as ex:
                Event(
                    ExceptionMessage(
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={"message": "node_sync "
                                 "os/cpu/memory sync failed: " +
                                 ex.message,
                                 "exception": ex}
                    )
                )
                NS.node_context = NS.node_context.load()
                NS.node_context.sync_status = "failed"
                NS.node_context.last_sync = str(time_utils.now())
                NS.node_context.status = "UP"
                NS.node_context.save(ttl=_sync_ttl)
                time.sleep(_sleep)

            sync_disks_thread = threading.Thread(target=disk_sync.sync)
            sync_disks_thread.daemon = True
            sync_disks_thread.start()
            sync_disks_thread.join()

            sync_networks_thread = threading.Thread(target=network_sync.sync)
            sync_networks_thread.daemon = True
            sync_networks_thread.start()
            sync_networks_thread.join()

            NS.node_context = NS.node_context.load()
            NS.node_context.sync_status = "done"
            NS.node_context.last_sync = str(time_utils.now())
            NS.node_context.status = "UP"
            NS.node_context.save(ttl=_sync_ttl)

            if "tendrl/monitor" not in NS.node_context.tags:
                sync_cluster_contexts_thread = threading.Thread(
                    target=cluster_contexts_sync.sync,
                    args=(_sync_ttl,)
                )
                sync_cluster_contexts_thread.daemon = True
                sync_cluster_contexts_thread.start()
                sync_cluster_contexts_thread.join()
            # Update node alert count
            if not NS.tendrl.objects.ClusterNodeAlertCounters().exists():
                update_cluster_node_alert_count()
            time.sleep(_sleep)
        logger.log(
            "info",
            NS.publisher_id,
            {"message": "%s complete" % self.__class__.__name__}
        )


def update_cluster_node_alert_count():
    alert_count = 0
    severity = ["WARNING", "CRITICAL"]
    try:
        if NS.tendrl_context.integration_id:
            alerts_arr = NS.tendrl.objects.NodeAlert(
                node_id=NS.node_context.node_id
            ).load_all()
            for alert in alerts_arr:
                if alert.severity in severity:
                    alert_count += 1
            NS.tendrl.objects.ClusterNodeAlertCounters(
                integration_id=NS.tendrl_context.integration_id,
                node_id=NS.node_context.node_id,
                alert_count=alert_count
            ).save()
    except EtcdException as ex:
        logger.log(
            "debug",
            NS.publisher_id,
            {"message": "Unable to update alert count.err: %s" % ex}
        )
