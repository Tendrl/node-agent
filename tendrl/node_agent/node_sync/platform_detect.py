import etcd

from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.utils import log_utils as logger
from tendrl.node_agent.discovery.platform import manager as platform_manager


def sync():
    try:
        # platform plugins
        logger.log(
            "debug",
            NS.publisher_id,
            {"message": "Running Platform detection"}
        )
        try:
            p_mgr = platform_manager.PlatformManager()
        except ValueError as ex:
            Event(
                ExceptionMessage(
                    priority="debug",
                    publisher=NS.publisher_id,
                    payload={
                        "message": 'Failed to init PlatformManager. '
                        '\\Error %s',
                        "exception": ex
                        }
                )
            )
            return
        # execute the platform plugins
        for plugin in p_mgr.get_available_plugins():
            platform_details = plugin.discover_platform()
            if len(platform_details.keys()) > 0:
                # update etcd
                try:
                    NS.platform = NS.tendrl.objects.Platform(
                        os=platform_details["Name"],
                        os_version=platform_details["OSVersion"],
                        kernel_version=platform_details["KernelVersion"],
                    )
                    NS.platform.save()

                except etcd.EtcdException as ex:
                    Event(
                        ExceptionMessage(
                            priority="debug",
                            publisher=NS.publisher_id,
                            payload={
                                "message": "Failed to update etcd . "
                                "\\Error %s",
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
                                    "OS Platform detection failed: " +
                                    ex.message,
                         "exception": ex}
            )
        )
