from etcd import EtcdException
from etcd import EtcdKeyNotFound

from tendrl.commons.objects.alert import AlertUtils
from tendrl.commons.objects.node_alert import NodeAlert
from tendrl.commons.objects.cluster_alert import ClusterAlert
from tendrl.commons.utils import etcd_utils
from tendrl.integrations.gluster import alerts as gluster_alert
from tendrl.node_agent.alert import constants
from tendrl.node_agent.objects.node_alert_counters import NodeAlertCounters
from tendrl.node_agent.objects.cluster_alert_counters import ClusterAlertCounters


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


def get_alerts(alert):
    alerts_arr = []
    try:
        if alert.classification == constants.NODE_ALERT:
            alerts = read(
                '/alerting/nodes/%s' % alert.node_id
            )
        elif  alert.classification == constants.CLUSTER_ALERT:
            alerts = read(
                '/alerting/clusters/%s' % alert.tags["integration_id"]
            ) 
    except EtcdKeyNotFound:
        return alerts_arr
    except (EtcdException, AttributeError) as ex:
        raise ex
    for alert_id, alert in alerts.iteritems():
        if alert:
            alerts_arr.append(AlertUtils().to_obj(alert))
    return alerts_arr


def classify_alert(alert, ttl=None):
    if alert.classification == constants.NODE_ALERT:
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
        ).save(ttl=ttl)
    elif alert.classification == constants.CLUSTER_ALERT:
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
        ).save(ttl=ttl)


def find_sds_name(integration_id):
    sds_name = NS.tendrl.objects.ClusterTendrlContext(
        integration_id=integration_id).load().sds_name
    return sds_name


def update_alert_count(alert, existing_alert):
    if alert.classification == constants.NODE_ALERT:
        counter_obj = NodeAlertCounters(
            node_id=alert.node_id
        ).load()
    elif alert.classification == constants.CLUSTER_ALERT:
        counter_obj = ClusterAlertCounters(
            integration_id=alert.tags['integration_id']
        ).load()
        sds_name = find_sds_name(
            alert.tags['integration_id']
        )
        if sds_name == constants.GLUSTER:
            gluster_alert.update_alert_count(
                alert, existing_alert
            )
    warn_count = int(counter_obj.warning_count)
    if existing_alert:
        if alert.severity == constants.ALERT_SEVERITY["info"]:
            warn_count -= 1
        elif alert.severity == constants.ALERT_SEVERITY["warning"]:
            warn_count += 1
    else:
        warn_count += 1
    counter_obj.warning_count = warn_count
    counter_obj.save()


def remove_alert(alert):
    try:
        alert_key = (
            '/alerting/alerts/%s' % alert.alert_id)
        if alert.classification == constants.NODE_ALERT:
            alert_classification_key = (
                '/alerting/nodes/%s/%s' % (
                    alert.node_id, alert.alert_id
                )
            )
        elif alert.classification == constants.CLUSTER_ALERT:
            alert_classification_key = (
                '/alerting/clusters/%s/%s' % (
                    alert.tags["integration_id"], alert.alert_id
                )
            )
        NS._int.client.delete(
            alert_key,
            recursive=True
        )
        NS._int.client.delete(
            alert_classification_key,
            recursive=True
        )
    except (etcd.EtcdConnectionFailed, etcd.EtcdException) as ex:
        if type(ex) != etcd.EtcdKeyNotFound:
            NS._int.wreconnect()
            NS._int.client.delete(
                alert_key,
                recursive=True
            )
            NS._int.client.delete(
                alert_classification_key,
                recursive=True
            )
        # For etcd_key_not_found, clearing alert may deleted by ttl
