from mock import patch

from tendrl.commons.message import Message as CommonMessage
from tendrl.commons.objects import BaseObject
from tendrl.node_agent.objects.cluster_message import ClusterMessage
from tendrl.node_agent.tests.test_init import init


def test_cluster_message():
    init()
    NS.config.data['message_retention_time'] = 10
    obj = ClusterMessage(
        priority="info",
        publisher="test",
        payload={"message": "testing"},
        integration_id="cd7b2732-bda2-4e3b-bc82-aefc2bc78de9",
        message_id="77deef29-b8e5-4dc5-8247-21e2a409a66a"
    )
    if not isinstance(obj, CommonMessage):
        raise AssertionError()
    with patch.object(BaseObject, "save") as save:
        save.return_value = True
        obj.save()
        save.assert_called()
    obj.render()
    if "cd7b2732-bda2-4e3b-bc82-aefc2bc78de9" not in obj.value and \
            "77deef29-b8e5-4dc5-8247-21e2a409a66a" not in obj.value:
        raise AssertionError(type(obj.value))
