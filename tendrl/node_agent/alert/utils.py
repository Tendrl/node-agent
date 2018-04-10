from etcd import EtcdConnectionFailed
from etcd import EtcdException
from etcd import EtcdKeyNotFound
from tendrl.integrations.gluster import alerts as gluster_alert
from tendrl.node_agent.alert import constants


def get_alerts(alert):
    alerts_arr = []
    try:
        if constants.NODE_ALERT in alert.classification:
            alerts_arr = NS.tendrl.objects.NodeAlert(
                node_id=alert.node_id
            ).load_all()
        elif constants.CLUSTER_ALERT in alert.classification:
            alerts_arr = NS.tendrl.objects.ClusterAlert(
                tags=alert.tags
            ).load_all()
    except EtcdKeyNotFound:
        return alerts_arr
    except (EtcdException, AttributeError) as ex:
        raise ex
    if alerts_arr:
        return alerts_arr
    else:
        return []


def classify_alert(alert, ttl=None):
    if constants.NODE_ALERT in alert.classification:
        NS.tendrl.objects.NodeAlert(
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
            acked_at=alert.acked_at,
            pid=alert.pid,
            source=alert.source,
            delivered=alert.delivered
        ).save(ttl=ttl)
    if constants.CLUSTER_ALERT in alert.classification:
        NS.tendrl.objects.ClusterAlert(
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
            acked_at=alert.acked_at,
            pid=alert.pid,
            source=alert.source,
            delivered=alert.delivered
        ).save(ttl=ttl)


def save_notification_only_alert(alert):
    NS.tendrl.objects.NotificationOnlyAlert(
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
        acked_at=alert.acked_at,
        pid=alert.pid,
        source=alert.source,
        delivered=alert.delivered
    ).save()


def find_sds_name(integration_id):
    sds_name = NS.tendrl.objects.ClusterTendrlContext(
        integration_id=integration_id).load().sds_name
    return sds_name


def update_alert_count(alert, existing_alert=None):
    if existing_alert:
        if(
            alert.severity == constants.ALERT_SEVERITY['warning'] and
            existing_alert.severity == constants.ALERT_SEVERITY['critical']
        ) or (
            alert.severity == constants.ALERT_SEVERITY['critical'] and
            existing_alert.severity == constants.ALERT_SEVERITY['warning']
        ):
            # no need to increment alert_count
            return
    if constants.NODE_ALERT in alert.classification:
        counter_obj = NS.tendrl.objects.NodeAlertCounters(
            node_id=alert.node_id
        ).load()
        update_count(alert, counter_obj)
        # Update cluster node alert count
        integration_id = alert.tags.get("integration_id", None)
        if integration_id:
            counter_obj = NS.tendrl.objects.ClusterNodeAlertCounters(
                node_id=alert.node_id,
                integration_id=alert.tags['integration_id']
            ).load()
            update_count(alert, counter_obj)
    if constants.CLUSTER_ALERT in alert.classification:
        counter_obj = NS.tendrl.objects.ClusterAlertCounters(
            integration_id=alert.tags['integration_id']
        ).load()
        if "sds_name" in alert.tags:
            sds_name = alert.tags["sds_name"]
        else:
            sds_name = find_sds_name(
                alert.tags['integration_id']
            )
        if sds_name == constants.GLUSTER:
            # volume alert count
            gluster_alert.update_alert_count(
                alert
            )
        update_count(alert, counter_obj)


def update_count(alert, counter_obj):
    alert_count = int(counter_obj.alert_count)
    if alert.severity == constants.ALERT_SEVERITY["info"]:
        alert_count -= 1
    elif alert.severity == constants.ALERT_SEVERITY["warning"]:
        alert_count += 1
    elif alert.severity == constants.ALERT_SEVERITY["critical"]:
        alert_count += 1
    counter_obj.alert_count = alert_count
    counter_obj.save()


def remove_alert(alert):
    alert_key = (
        '/alerting/alerts/%s' % alert.alert_id)
    remove(alert_key)
    if constants.NODE_ALERT in alert.classification:
        alert_classification_key = (
            '/alerting/nodes/%s/%s' % (
                alert.node_id, alert.alert_id
            )
        )
        remove(alert_classification_key)
    if constants.CLUSTER_ALERT in alert.classification:
        alert_classification_key = (
            '/alerting/clusters/%s/%s' % (
                alert.tags["integration_id"], alert.alert_id
            )
        )
        remove(alert_classification_key)


def remove(key):
    try:
        NS._int.client.delete(
            key,
            recursive=True
        )
    except (EtcdConnectionFailed, EtcdException) as ex:
        if type(ex) != EtcdKeyNotFound:
            NS._int.wreconnect()
            NS._int.client.delete(
                key,
                recursive=True
            )
        # For etcd_key_not_found, clearing alert may deleted by ttl
