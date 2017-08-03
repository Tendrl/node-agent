import gevent

from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.message import Message
from tendrl.commons import sds_sync
from tendrl.commons.utils import time_utils

from tendrl.node_agent.node_sync import cluster_contexts_sync
from tendrl.node_agent.node_sync import disk_sync
from tendrl.node_agent.node_sync import network_sync
from tendrl.node_agent.node_sync import platform_detect
from tendrl.node_agent.node_sync import sds_detect
from tendrl.node_agent.node_sync import services_and_index_sync


class NodeAgentSyncThread(sds_sync.StateSyncThread):
    def _run(self):
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "%s running" % self.__class__.__name__}
            )
        )
        _init_monitoring = False
        while not self._complete.is_set():
            if not _init_monitoring:
                try:
                    from tendrl.monitoring_integration import main
                    main()
                    _init_monitoring = True
                except ImportError:
                    pass
                    
            gevent.sleep(int(NS.config.data.get("sync_interval", 10)))
            NS.node_context = NS.node_context.load()
            NS.node_context.sync_status = "in_progress"
            NS.node_context.save()
            NS.tendrl_context = NS.tendrl_context.load()

            sync_service_and_index_thread = gevent.spawn(
                services_and_index_sync.sync)
            sync_service_and_index_thread.join()

            platform_detect_thread = gevent.spawn(platform_detect.sync)
            sds_detect_thread = gevent.spawn(sds_detect.sync)
            gevent.joinall([platform_detect_thread, sds_detect_thread])

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
                NS.node_context.save()

            sync_disks_thread = gevent.spawn(disk_sync.sync)
            sync_disks_thread.join()

            sync_networks_thread = gevent.spawn(network_sync.sync)
            sync_networks_thread.join()

            NS.node_context = NS.node_context.load()
            NS.node_context.sync_status = "done"
            NS.node_context.last_sync = str(time_utils.now())
            NS.node_context.save()

            sync_cluster_contexts_thread = gevent.spawn(
                cluster_contexts_sync.sync)
            sync_cluster_contexts_thread.join()

        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "%s complete" % self.__class__.__name__}
            )
        )
