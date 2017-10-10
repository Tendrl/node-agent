import threading
import time

from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.message import Message
from tendrl.commons import sds_sync
from tendrl.commons.utils import time_utils

from tendrl.node_agent.node_sync import check_all_managed_nodes_status
from tendrl.node_agent.node_sync import cluster_contexts_sync
from tendrl.node_agent.node_sync import disk_sync
from tendrl.node_agent.node_sync import network_sync
from tendrl.node_agent.node_sync import platform_detect
from tendrl.node_agent.node_sync import sds_detect
from tendrl.node_agent.node_sync import services_and_index_sync


class NodeAgentSyncThread(sds_sync.StateSyncThread):
    def run(self):
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "%s running" % self.__class__.__name__}
            )
        )

        NS.node_context = NS.node_context.load()
        current_tags = list(NS.node_context.tags)
        current_tags += ["tendrl/node_%s" % NS.node_context.node_id]
        NS.node_context.tags = list(set(current_tags))
        NS.node_context.save()
        _sync_ttl = int(NS.config.data.get("sync_interval", 10)) + 100
        while not self._complete.is_set():
            time.sleep(int(NS.config.data.get("sync_interval", 10)))
            NS.node_context = NS.node_context.load()
            NS.node_context.sync_status = "in_progress"
            NS.node_context.save(ttl=_sync_ttl)
            NS.tendrl_context = NS.tendrl_context.load()

            platform_detect_thread = threading.Thread(
                target=platform_detect.sync)
            platform_detect.daemon = True
            platform_detect_thread.start()
            sds_detect_thread = threading.Thread(target=sds_detect.sync)
            sds_detect_thread.daemon = True
            sds_detect_thread.start()

            sync_service_and_index_thread = threading.Thread(
                target=services_and_index_sync.sync, args=(_sync_ttl,))
            sync_service_and_index_thread.daemon = True
            sync_service_and_index_thread.start()

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
                NS.node_context.save(ttl=_sync_ttl)

            sync_disks_thread = threading.Thread(target=disk_sync.sync)
            sync_disks_thread.daemon = True
            sync_disks_thread.start()

            sync_networks_thread = threading.Thread(target=network_sync.sync)
            sync_networks_thread.daemon = True
            sync_networks_thread.start()

            if "tendrl/monitor" in NS.node_context.tags:
                check_all_managed_node_status_thread = threading.Thread(
                    target=check_all_managed_nodes_status.run)
                check_all_managed_node_status_thread.daemon = True
                check_all_managed_node_status_thread.start()

            NS.node_context = NS.node_context.load()
            NS.node_context.sync_status = "done"
            NS.node_context.last_sync = str(time_utils.now())
            NS.node_context.save(ttl=_sync_ttl)

            sync_cluster_contexts_thread = threading.Thread(
                target=cluster_contexts_sync.sync, args=(_sync_ttl,))
            sync_cluster_contexts_thread.daemon = True
            sync_cluster_contexts_thread.start()

        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "%s complete" % self.__class__.__name__}
            )
        )
