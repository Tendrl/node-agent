import etcd

from tendrl.commons.event import Event
from tendrl.commons.message import Message, ExceptionMessage

from tendrl.node_agent.discovery.platform import manager as platform_manager


def load_and_execute_platform_discovery_plugins():
    # platform plugins
    Event(
        Message(
            priority="debug",
            publisher=NS.publisher_id,
            payload={"message": "load_and_execute_platform_discovery_plugins, "
                                "platform plugins"
                     }
        )
    )
    try:
        pMgr = platform_manager.PlatformManager()
    except ValueError as ex:
        Event(
            ExceptionMessage(
                priority="error",
                publisher=NS.publisher_id,
                payload={
                    "message": 'Failed to init PlatformManager. \Error %s',
                    "exception": ex
                    }
            )
        )
        return
    # execute the platform plugins
    for plugin in pMgr.get_available_plugins():
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
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={
                            "message": "Failed to update etcd . \Error %s",
                            "exception": ex
                        }
                    )
                )
            break
