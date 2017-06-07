import gevent
import json
import os

from tendrl.commons.event import Event
from tendrl.commons.message import Message, ExceptionMessage
from tendrl.commons.utils import cmd_utils
from tendrl.commons import sds_sync
from tendrl.commons.utils import log_utils as logger
from tendrl.node_agent.node_sync import disk_sync


class CephIntegrtaionsSyncThread(sds_sync.StateSyncThread):
    def _run(self):
        logger.log(
            "debug",
            NS.get("publisher_id", None),
            {"message": "%s running" % self.__class__.__name__}
        )
        if NS.tendrl_context.integration_id is not None:
            while not self._complete.is_set():
                # sync of OSD journal details every 30 sec is fine
                # as this data doesnt change very frequently in cluster
                gevent.sleep(30)
                try:
                    # Sync the OSD journal details
                    logger.log(
                        "debug",
                        NS.get("publisher_id", None),
                        {"message": "ceph_integrations_sync, osd journal details"}
                    )
                    journal_details = {}
                    osd_path = "/var/lib/ceph/osd"
                    osd_list = os.listdir("/var/lib/ceph/osd")

                    if len(osd_list) > 0:
                        for item in os.listdir(osd_path):
                            journal_path = "%s/%s/journal" % (osd_path, item)
                            out, err, rc = cmd_utils.Command(
                                "lsblk -o PKNAME,ROTA -n %s" % journal_path
                            ).run()
                            if rc != 0:
                                logger.log(
                                    "error",
                                    NS.get("publisher_id", None),
                                    {"message": "Error getting journal details for OSD. Error: %s" % err}
                                )
                            else:
                                journal_disk, rotational = out.split()
                                if ("/dev/%s" % journal_disk) in journal_details.keys():
                                    journal_details[
                                        "/dev/%s" % journal_disk
                                    ]['journal_count'] += 1
                                    journal_details[
                                        "/dev/%s" % journal_disk
                                    ]['ssd'] = disk_sync.is_ssd(rotational)
                                else:
                                    journal_details["/dev/%s" % journal_disk] = {
                                        'journal_count': 1,
                                        'ssd': disk_sync.is_ssd(rotational)
                                    }

                        NS.integrations.ceph.objects.Journal(
                            integration_id=NS.tendrl_context.integration_id,
                            node_id=NS.node_context.node_id,
                            data=json.dumps(journal_details)
                        ).save(update=False)
                except Exception as ex:
                    logger.log(
                        "error",
                        NS.get("publisher_id", None),
                        {
                            "message": "ceph integrations sync failed: " + ex.message,
                            "exception": ex
                        }
                    )

            logger.log(
                "debug",
                NS.get("publisher_id", None),
                {"message": "%s complete" % self.__class__.__name__}
            )
