from tendrl.node_agent.alert import constants

VOLUME_ALERT = "volume_utilization_alert"


def update_alert_count(alert, existing_alert):
    if alert.resource == VOLUME_ALERT:    
        counter_obj = NS.integrations.gluster.objects.VolumeAlertCounters(
            integration_id=alert.tags['integration_id'],
            volume_id=alert.tags['volume_id']
        ).load()
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
