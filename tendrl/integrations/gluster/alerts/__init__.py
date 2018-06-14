from tendrl.node_agent.alert import constants


def update_alert_count(alert):
    if alert.resource in NS.integrations.gluster.objects.VolumeAlertCounters(
            )._defs['relationship'][alert.alert_type.lower()]:
        volume = find_volume_id(
            alert.tags['volume_name'],
            alert.tags['integration_id']
        )
        if volume and (
            volume.vol_id not in [None, ''] or volume.name is not None
        ):
            alert.tags['volume_id'] = volume.vol_id
            counter_obj = \
                NS.integrations.gluster.objects.VolumeAlertCounters(
                    integration_id=alert.tags['integration_id'],
                    volume_id=alert.tags['volume_id']
                ).load()
            alert_count = int(counter_obj.alert_count)
            if alert.severity == constants.ALERT_SEVERITY["info"]:
                alert_count -= 1
            elif alert.severity == constants.ALERT_SEVERITY["warning"]:
                alert_count += 1
            elif alert.severity == constants.ALERT_SEVERITY["critical"]:
                alert_count += 1
            counter_obj.alert_count = alert_count
            counter_obj.save()


def find_volume_id(vol_name, integration_id):
    volumes = NS.tendrl.objects.GlusterVolume(
        integration_id
    ).load_all()
    for volume in volumes:
        if volume.name == vol_name:
            return volume
