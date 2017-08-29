import json

from etcd import EtcdException
from etcd import EtcdKeyNotFound

from tendrl.commons.objects.alert import AlertUtils
from tendrl.commons.utils import log_utils as logger
from tendrl.node_agent.alert import utils

SUPPORTED_ALERT_TYPES = [
    "utilization",
    "status"
]


class InvalidAlertType(Exception):
    pass


def update_alert(msg_id, alert_str):
    try:
        existing_alert = False
        new_alert = json.loads(alert_str)
        new_alert['alert_id'] = msg_id
        new_alert_obj = AlertUtils().to_obj(new_alert)
        if not new_alert_obj.alert_type in SUPPORTED_ALERT_TYPES:
            logger.log(
                "error",
                NS.publisher_id,
                {
                    "message": "Invalid alert type in alert %s" % alert_str
                }    
            )
            raise InvalidAlertType    
        alerts = utils.get_alerts()
        for curr_alert in alerts:
            if AlertUtils().is_same(new_alert_obj, curr_alert):
                new_alert_obj = AlertUtils().update(
                    new_alert_obj,
                    curr_alert
                )
                if not AlertUtils().equals(
                    new_alert_obj,
                    curr_alert
                ):
                    new_alert_obj.save()
                    utils.classify_alert(new_alert_obj)
                    existing_alert = True
                    utils.update_alert_count(
                        new_alert_obj,
                        existing_alert
                    )
                    return
                return
            # else add this new alert to etcd
        new_alert_obj.save()
        utils.classify_alert(new_alert_obj)
        utils.update_alert_count(
            new_alert_obj,
            existing_alert
        )
    except(
        ValueError,
        KeyError,
        InvalidAlertType, 
        EtcdKeyNotFound,
        EtcdException
    ) as ex:
        logger.log(
            "error",
            NS.publisher_id,
            {
                "message": "Error in updating alert %s" % alert_str
            }
        )
