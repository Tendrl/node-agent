from etcd import EtcdException
from etcd import EtcdKeyNotFound

from tendrl.commons.objects.alert import AlertUtils
from tendrl.commons.objects.node_alert import NodeAlert
from tendrl.commons.objects.cluster_alert import ClusterAlert
from tendrl.commons.utils import etcd_utils
from tendrl.integrations.gluster import utils
from tendrl.node_agent.objects.node_alert_counters import NodeAlertCounters
from tendrl.node_agent.objects.cluster_alert_counters import ClusterAlertCounters

NODE_ALERT = "node"
CLUSTER_ALERT = "cluster"
ALERT_SEVERITY = {
    "info" : "INFO",
    "warning": "WARNING"
}

def read(key):
    result = {}
    obj = {}
    try:
        obj = etcd_utils.read(key)
    except EtcdKeyNotFound:
        pass
    except (AttributeError, EtcdException) as ex:
        raise ex
    if hasattr(obj, 'leaves'):
        for item in obj.leaves:
            if key == item.key:
                result[item.key.split("/")[-1]] = item.value
                return result
            if item.dir is True:
                result[item.key.split("/")[-1]] = read(item.key)
            else:
                result[item.key.split("/")[-1]] = item.value
    return result


def get_alerts():
    alerts_arr = []
    try:
        alerts = read('/alerting/alerts')
    except EtcdKeyNotFound:
        return alerts_arr
    except (EtcdException, AttributeError) as ex:
        raise ex
    for alert_id, alert in alerts.iteritems():
        alerts_arr.append(AlertUtils().to_obj(alert))
    return alerts_arr


def classify_alert(alert):
    if alert.classification == "node":
        NodeAlert(
            alert_id=alert.alert_id,
            node_id=alert.node_id,
            time_stamp=alert.time_stamp,
            resource=alert.resource,
            current_value=alert.current_value,
            tags=alert.tags,
            alert_type=alert.alert_type,
            severity=alert.severity,
            classification=alert.classification,
            significance=alert.significance,
            ackedby=alert.ackedby,
            acked=alert.acked,
            ack_comment=alert.ack_comment,
            acked_at = alert.acked_at,
            pid=alert.pid,
            source=alert.source,
            delivered=alert.delivered
        ).save()
    elif alert.classification == "cluster":
        ClusterAlert(
            alert_id=alert.alert_id,
            node_id=alert.node_id,
            time_stamp=alert.time_stamp,
            resource=alert.resource,
            current_value=alert.current_value,
            tags=alert.tags,
            alert_type=alert.alert_type,
            severity=alert.severity,
            classification=alert.classification,
            significance=alert.significance,
            ackedby=alert.ackedby,
            acked=alert.acked,
            ack_comment=alert.ack_comment,
            acked_at = alert.acked_at,
            pid=alert.pid,
            source=alert.source,
            delivered=alert.delivered
        ).save()

def update_alert_count(alert, existing_alert):
    if alert.classification == NODE_ALERT:
       counter_obj = NodeAlertCounters(
            node_id=alert.node_id).load()
    elif alert.classification == CLUSTER_ALERT:
        counter_obj = ClusterAlertCounters(
            integration_id=alert.tags['integration_id']
        ).load()
        if alert.resource == "volume_utilization_alert":
            utils.update_volume_alert_count(alert, existing_alert)

    warn_count = int(counter_obj.warning_count)
    info_count = int(counter_obj.info_count)
    if existing_alert:
        if alert.severity == ALERT_SEVERITY["info"]:
            warn_count -= 1
            info_count += 1 
        elif alert.severity == ALERT_SEVERITY["warning"]:
            warn_count += 1
            info_count -= 1
    else:
        if alert.severity == ALERT_SEVERITY["info"]:
            info_count += 1
        else:
            warn_count += 1
    counter_obj.warning_count = warn_count
    counter_obj.info_count = info_count
    counter_obj.save()
