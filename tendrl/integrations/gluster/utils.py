def update_volume_alert_count(alert, existing_alert):
    counter_obj = NS.integrations.gluster.objects.VolumeAlertCounters(
        integration_id=alert.tags['integration_id'],
        volume_id=alert.tags['volume_id']
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
