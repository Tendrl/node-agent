import collectd
import traceback
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree

import tendrl_glusterfs_base
import glusterfs.utils as tendrl_glusterfs_utils


class TendrlGlusterfsProfileInfo(
    tendrl_glusterfs_base.TendrlGlusterfsMonitoringBase
):
    def __init__(self):
        tendrl_glusterfs_base.TendrlGlusterfsMonitoringBase.__init__(self)

    def _parseVolumeProfileInfo(self, tree, nfs=False):
        bricks = []
        if nfs:
            brickKey = 'nfs'
            bricksKey = 'nfsServers'
        else:
            brickKey = 'brick'
            bricksKey = 'bricks'
        for brick in tree.findall('volProfile/brick'):
            fopCumulative = []
            blkCumulative = []
            fopInterval = []
            blkInterval = []
            brickName = brick.find('brickName').text
            for block in brick.findall('cumulativeStats/blockStats/block'):
                blkCumulative.append(
                    {
                        'size': block.find('size').text,
                        'read': block.find('reads').text,
                        'write': block.find('writes').text
                    }
                )
            for fop in brick.findall('cumulativeStats/fopStats/fop'):
                fopCumulative.append(
                    {
                        'name': fop.find('name').text,
                        'hits': fop.find('hits').text,
                        'latencyAvg': fop.find('avgLatency').text,
                        'latencyMin': fop.find('minLatency').text,
                        'latencyMax': fop.find('maxLatency').text
                    }
                )
            for block in brick.findall('intervalStats/blockStats/block'):
                blkInterval.append(
                    {
                        'size': block.find('size').text,
                        'read': block.find('reads').text,
                        'write': block.find('writes').text
                    }
                )
            for fop in brick.findall('intervalStats/fopStats/fop'):
                fopInterval.append(
                    {
                        'name': fop.find('name').text,
                        'hits': fop.find('hits').text,
                        'latencyAvg': fop.find('avgLatency').text,
                        'latencyMin': fop.find('minLatency').text,
                        'latencyMax': fop.find('maxLatency').text
                    }
                )
            bricks.append(
                {
                    brickKey: brickName,
                    'cumulativeStats': {
                        'blockStats': blkCumulative,
                        'fopStats': fopCumulative,
                        'duration': brick.find('cumulativeStats/duration').text,
                        'totalRead': brick.find('cumulativeStats/totalRead').text,
                        'totalWrite': brick.find('cumulativeStats/totalWrite').text
                    },
                    'intervalStats': {
                        'blockStats': blkInterval,
                        'fopStats': fopInterval,
                        'duration': brick.find('intervalStats/duration').text,
                        'totalRead': brick.find('intervalStats/totalRead').text,
                        'totalWrite': brick.find('intervalStats/totalWrite').text
                    }
                }
            )
        status = {
            'volumeName': tree.find("volProfile/volname").text,
            bricksKey: bricks
        }
        return status

    def get_volume_profile_info(self, volName):
        ret_val = {}
        brickName = ''
        profile_info = {}
        profile_cmd_op, profile_err = tendrl_glusterfs_utils.exec_command(
            "gluster volume profile %s info --xml" % volName
        )
        if profile_err:
            collectd.error(
                'Failed to fetch brick utilizations. The error is: %s' % (
                    profile_err
                )
            )
            return ret_val
        try:
            profile_info = self._parseVolumeProfileInfo(
                ElementTree.fromstring(profile_cmd_op)
            )
            return profile_info
        except (
            AttributeError,
            KeyError,
            ValueError
        ):
            collectd.error(
                'Failed to collect iops details of brick %s in volume %s of '
                'cluster %s. The profile info is %s. Error %s' % (
                    brickName,
                    volName,
                    self.CONFIG['integration_id'],
                    str(profile_info),
                    traceback.format_exc()
                )
            )
            return ret_val

    def get_metrics(self):
        ret_val = {}
        volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
        for volume in volumes:
            volName = volume['name']
            vol_iops = self.get_volume_profile_info(volName)
            for brick_det in vol_iops.get('bricks'):
                brickName = brick_det.get('brick')
                ret_val[
                    "clusters.%s.volumes.%s.nodes.%s.bricks.%s.iops.gauge-read" % (
                        self.CONFIG['integration_id'],
                        volName,
                        brickName.split(':')[0].replace('.', '_'),
                        brickName.split(':')[1].replace('/', '|')
                    )
                ] = brick_det.get('cumulativeStats').get('totalRead')
                ret_val[
                    "clusters.%s.volumes.%s.nodes.%s.bricks.%s.iops.gauge-write" % (
                        self.CONFIG['integration_id'],
                        volName,
                        brickName.split(':')[0].replace('.', '_'),
                        brickName.split(':')[1].replace('/', '|')
                    )
                ] = brick_det.get('cumulativeStats').get('totalWrite')
        return ret_val
