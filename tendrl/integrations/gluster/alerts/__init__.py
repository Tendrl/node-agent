from etcd import EtcdKeyNotFound

from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger
from tendrl.node_agent.alert import constants


def update_alert_count(alert, existing_alert):
    if alert.resource in NS.integrations.gluster.objects.VolumeAlertCounters(
            )._defs['relationship'][alert.alert_type.lower()]:
        alert.tags['volume_id'] = find_volume_id(
            alert.tags['volume_name'],
            alert.tags['integration_id']
        )
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


def find_volume_id(vol_name, integration_id):
    try:
        volumes = etcd_utils.read(
            "clusters/%s/Volumes" % integration_id
        )
        for volume in volumes.leaves:
            key = volume.key + "/name"
            name = etcd_utils.read(key).value
            if vol_name == name:
                return volume.key.split("/")[-1]
    except (EtcdKeyNotFound) as ex:
        logger.log(
            "error",
            NS.publisher_id,
            {
                "message": "Failed to fetch volume id for volume name %s" %
                vol_name
            }
        )
        raise ex
