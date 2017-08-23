from etcd import EtcdException
from etcd import EtcdKeyNotFound

from tendrl.commons.objects.alert import AlertUtils
from tendrl.commons.objects.node_alert import NodeAlert
from tendrl.commons.objects.cluster_alert import ClusterAlert
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
            ).save()
