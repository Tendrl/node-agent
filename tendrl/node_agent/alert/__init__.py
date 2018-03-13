import json

from etcd import EtcdException
from etcd import EtcdKeyNotFound
from etcd import Lock

from tendrl.commons.objects.alert import AlertUtils
from tendrl.commons.utils import log_utils as logger
from tendrl.node_agent.alert import constants
from tendrl.node_agent.alert import utils


class InvalidAlertType(Exception):
    pass


class InvalidAlertSeverity(Exception):
    pass


def update_alert(message):
    try:
        lock = None
        existing_alert = False
        new_alert = json.loads(message.payload["message"])
        new_alert['alert_id'] = message.message_id
        new_alert_obj = AlertUtils().to_obj(new_alert)
        if new_alert_obj.alert_type not in constants.SUPPORTED_ALERT_TYPES:
            logger.log(
                "error",
                NS.publisher_id,
                {
                    "message": "Invalid alert type in alert %s" % new_alert
                }
            )
            raise InvalidAlertType
        if new_alert_obj.severity not in constants.SUPPORTED_ALERT_SEVERITY:
            logger.log(
                "error",
                NS.publisher_id,
                {
                    "message": "Invalid alert severity in alert %s" % new_alert
                }
            )
            raise InvalidAlertSeverity
        alert_notify = message.payload.get('alert_notify', False)
        if not alert_notify:
            if (new_alert_obj.resource in
                NS.tendrl.objects.ClusterAlert()._defs['relationship'][
                    new_alert_obj.alert_type.lower()]):
                new_alert_obj.classification.append(constants.CLUSTER_ALERT)
            if (new_alert_obj.resource in
                NS.tendrl.objects.NodeAlert()._defs['relationship'][
                    new_alert_obj.alert_type.lower()]):
                new_alert_obj.classification.append(constants.NODE_ALERT)
            alerts = utils.get_alerts(new_alert_obj)
            for curr_alert in alerts:
                curr_alert.tags = json.loads(curr_alert.tags)
                if AlertUtils().is_same(new_alert_obj, curr_alert):
                    if new_alert_obj.severity == constants.ALERT_SEVERITY["info"]:
                        if "clear_alert" in new_alert_obj.tags.keys():
                            if new_alert_obj.tags['clear_alert'] != \
                                    curr_alert.severity:
                                # only warning clearing alert can clear the warning alert
                                # and critical clearing alert can clear the critical alert
                                # Because critical/warning alert panels in grafana
                                # are indipendent from one another, So after critical
                                # alert raised if warning clearing came then tendrl
                                # can show only clearing alert, So this logic will help
                                # to prevent from the above case.
                                return
                    new_alert_obj = AlertUtils().update(
                        new_alert_obj,
                        curr_alert
                    )
                    if not AlertUtils().equals(
                        new_alert_obj,
                        curr_alert
                    ):
                        # Lock only if new alert matches with existing alert
                        lock = Lock(
                            NS._int.wclient,
                            'alerting/alerts/%s' % new_alert_obj.alert_id
                        )
                        lock.acquire(blocking=True,
                                     lock_ttl=60)
                        if lock.is_acquired:
                            # renew a lock
                            lock.acquire(lock_ttl=60)
                        utils.update_alert_count(
                            new_alert_obj,
                            curr_alert
                        )
                        if message.payload["alert_condition_unset"]:
                            keep_alive = int(
                                NS.config.data["alert_retention_time"]
                            )
                            utils.classify_alert(new_alert_obj, keep_alive)
                            new_alert_obj.save(ttl=keep_alive)
                        else:
                            # Remove the clearing alert with same if exist
                            utils.remove_alert(new_alert_obj)
                            utils.classify_alert(new_alert_obj)
                            new_alert_obj.save()
                        return
                    else:
                        # Handle case where alert severity changes without
                        # coming to normal. In this case the previous alert
                        # should be overriden with new one
                        utils.remove_alert(new_alert_obj)
                        utils.classify_alert(new_alert_obj)
                        new_alert_obj.save()
                    return
                # else add this new alert to etcd
            if message.payload["alert_condition_state"] == \
                constants.ALERT_SEVERITY["warning"]:
                utils.update_alert_count(
                    new_alert_obj
                )
                utils.classify_alert(new_alert_obj)
                new_alert_obj.save()
            else:
                logger.log(
                    "debug",
                    NS.publisher_id,
                    {
                        "message": "New alert can't be a clearing alert %s" % (
                            new_alert
                        )
                    }
                )
        else:
            # SDS native events
            utils.save_notification_only_alert(new_alert_obj)
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
                    ex, new_alert
                )
            }
        )
    finally:
        if isinstance(lock, Lock) and lock.is_acquired:
            lock.release()
