import json

from etcd import EtcdException
from etcd import EtcdKeyNotFound

from tendrl.commons.objects.alert import AlertUtils
from tendrl.commons.utils import log_utils as logger
from tendrl.node_agent.alert import constants
from tendrl.node_agent.alert import utils


class InvalidAlertType(Exception):
    pass


class InvalidAlertSeverity(Exception):
    pass


def update_alert(msg_id, alert_str):
    try:
        existing_alert = False
        new_alert = json.loads(alert_str)
        new_alert['alert_id'] = msg_id
        new_alert_obj = AlertUtils().to_obj(new_alert)
        if new_alert_obj.alert_type not in constants.SUPPORTED_ALERT_TYPES:
            logger.log(
                "error",
                NS.publisher_id,
                {
                    "message": "Invalid alert type in alert %s" % alert_str
                }
            )
            raise InvalidAlertType
        if new_alert_obj.severity not in constants.SUPPORTED_ALERT_SEVERITY:
            logger.log(
                "error",
                NS.publisher_id,
                {
                    "message": "Invalid alert severity in alert %s" % alert_str
                }
            )
            raise InvalidAlertSeverity
        alerts = utils.get_alerts(new_alert_obj)
        for curr_alert in alerts:
            curr_alert.tags = json.loads(curr_alert.tags)
            if AlertUtils().is_same(new_alert_obj, curr_alert):
                new_alert_obj = AlertUtils().update(
                    new_alert_obj,
                    curr_alert
                )
                if not AlertUtils().equals(
                    new_alert_obj,
                    curr_alert
                ):
                    existing_alert = True
                    utils.update_alert_count(
                        new_alert_obj,
                        existing_alert
                    )
                    if new_alert_obj.severity == \
                        constants.ALERT_SEVERITY["info"]:
                        keep_alive = int(
                            NS.config.data["alert_retention_time"]
                        )
                        utils.classify_alert(new_alert_obj, keep_alive)
                        new_alert_obj.save(ttl=keep_alive)
                    elif new_alert_obj.severity == \
                        constants.ALERT_SEVERITY["warning"]:
                        # Remove the clearing alert with same if exist
                        utils.remove_alert(new_alert_obj)
                        utils.classify_alert(new_alert_obj)
                        new_alert_obj.save()
                    return
                return
            # else add this new alert to etcd
        utils.update_alert_count(
            new_alert_obj,
            existing_alert
        )
        utils.classify_alert(new_alert_obj)
        new_alert_obj.save()
    except(
        AttributeError,
        TypeError,
        ValueError,
        KeyError,
        InvalidAlertType,
        InvalidAlertSeverity,
        EtcdKeyNotFound,
        EtcdException
    ) as ex:
        logger.log(
            "error",
            NS.publisher_id,
            {
                "message": "Error %s in updating alert %s" % (
                    ex, alert_str
                )
            }
        )
