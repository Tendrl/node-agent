from etcd import EtcdException
from etcd import EtcdKeyNotFound

from tendrl.commons.objects.alert import AlertUtils
from tendrl.commons.objects.node_alert import NodeAlert
from tendrl.commons.objects.cluster_alert import ClusterAlert
from tendrl.commons.objects.node_alert_counters import NodeAlertCounters
from tendrl.commons.objects.cluster_alert_counters import ClusterAlertCounters
from tendrl.commons.utils import etcd_utils

def read(key):
    result = {}
    job = {}
    try:
        job = etcd_utils.read(key)
    except EtcdKeyNotFound:
        pass
    except (AttributeError, EtcdException) as ex:
        raise ex
    if hasattr(job, 'leaves'):
        for item in job.leaves:
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
    if 'alert_catagory' in alert.tags:
        if alert.tags['alert_catagory'] == "node":
            NodeAlert(
                alert_id=alert.alert_id,
                node_id=alert.node_id,
                time_stamp=alert.time_stamp,
                resource=alert.resource,
                current_value=alert.current_value,
                tags=alert.tags,
                alert_type=alert.alert_type,
                severity=alert.severity,
                significance=alert.significance,
                ackedby=alert.ackedby,
                acked=alert.acked,
                ack_comment=alert.ack_comment,
                acked_at = alert.acked_at,
                pid=alert.pid,
                source=alert.source,
                delivered=alert.delivered
            ).save()
        elif alert.tags['alert_catagory'] == "cluster":
            ClusterAlert(
                alert_id=alert.alert_id,
                node_id=alert.node_id,
                time_stamp=alert.time_stamp,
                resource=alert.resource,
                current_value=alert.current_value,
                tags=alert.tags,
                alert_type=alert.alert_type,
                severity=alert.severity,
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
    if alert.tags['alert_catagory'] == "node":
        counter_obj = NodeAlertCounters(
            node_id=alert.node_id).load()
    elif alert.tags['alert_catagory'] == "cluster":
        counter_obj = ClusterAlertCounters(
            integration_id=alert.tags['integration_id']
        ).load()
    
    warn_count = int(counter_obj.warning_count)
    info_count = int(counter_obj.info_count)
    if existing_alert:
        if alert.severity == "INFO":
            warn_count -= 1
            info_count += 1 
        elif alert.severity == "WARNING":
            warn_count += 1
            info_count -= 1
    else:
        if alert.severity == "INFO":
            info_count += 1
        else:
            warn_count += 1
    counter_obj.warning_count = warn_count
    counter_obj.info_count = info_count
    counter_obj.save()
