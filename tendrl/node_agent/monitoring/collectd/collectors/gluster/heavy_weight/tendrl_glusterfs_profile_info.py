import collectd
import etcd
import json
import math
import time
import traceback
# import threading

try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree


import heavy_weight.tendrl_gluster_heal_info as tendrl_gluster_heal_info
from tendrl_gluster import TendrlGlusterfsMonitoringBase
import utils as tendrl_glusterfs_utils


READ_WRITE_OPS = [
    'CREATE',
    'DISCARD',
    'FALLOCATE',
    'FLUSH',
    'FSYNC',
    'FSYNCDIR',
    'RCHECKSUM',
    'READ',
    'READDIR',
    'READDIRP',
    'READY',
    'WRITE',
    'ZEROFILL'
]
LOCK_OPS = [
    'ENTRYLK',
    'FENTRYLK',
    'FINODELK',
    'INODELK',
    'LK'
]
INODE_OPS = [
    'ACCESS',
    'FGETXATTR',
    'FREMOVEXATTR',
    'FSETATTR',
    'FSETXATTR',
    'FSTAT',
    'FTRUNCATE',
    'FXATTROP',
    'GETXATTR',
    'LOOKUP',
    'OPEN',
    'OPENDIR',
    'READLINK',
    'REMOVEXATTR',
    'SEEK',
    'SETATTR',
    'SETXATTR',
    'STAT',
    'STATFS',
    'TRUNCATE',
    'XATTROP'
]
ENTRY_OPS = [
    'LINK',
    'MKDIR',
    'MKNOD',
    'RENAME',
    'RMDIR',
    'SYMLINK',
    'UNLINK'
]


class TendrlHealInfoAndProfileInfoPlugin(
    TendrlGlusterfsMonitoringBase
):
    etcd_client = {}

    def __init__(self):
        self.provisioner_only_plugin = True
        self.brick_path_repl = self.CONFIG['brick_path_replace']
        TendrlGlusterfsMonitoringBase.__init__(self)

        if not self.etcd_client:
            _etcd_args = dict(
                host=self.CONFIG['etcd_host'],
                port=int(self.CONFIG['etcd_port'])
            )
            etcd_ca_cert_file = self.CONFIG.get("etcd_ca_cert_file")
            etcd_cert_file = self.CONFIG.get("etcd_cert_file")
            etcd_key_file = self.CONFIG.get("etcd_key_file")
            if (
                etcd_ca_cert_file and
                str(etcd_ca_cert_file) != "" and
                etcd_cert_file and
                str(etcd_cert_file) != "" and
                etcd_key_file and
                str(etcd_key_file) != ""
            ):
                _etcd_args.update(
                    {
                        "ca_cert": str(self.CONFIG['etcd_ca_cert_file']),
                        "cert": (
                            str(self.CONFIG['etcd_cert_file']),
                            str(self.CONFIG['etcd_key_file'])
                        ),
                        "protocol": "https"
                    }
                )
            self.etcd_client = etcd.Client(**_etcd_args)

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
                        'duration': brick.find(
                            'cumulativeStats/duration'
                        ).text,
                        'totalRead': brick.find(
                            'cumulativeStats/totalRead'
                        ).text,
                        'totalWrite': brick.find(
                            'cumulativeStats/totalWrite'
                        ).text
                    },
                    'intervalStats': {
                        'blockStats': blkInterval,
                        'fopStats': fopInterval,
                        'duration': brick.find('intervalStats/duration').text,
                        'totalRead': brick.find(
                            'intervalStats/totalRead'
                        ).text,
                        'totalWrite': brick.find(
                            'intervalStats/totalWrite'
                        ).text
                    }
                }
            )
        status = {
            'volumeName': tree.find("volProfile/volname").text,
            bricksKey: bricks
        }
        return status

    def get_volume_profile_info(self, volName, cluster_id):
        ret_val = {}
        brickName = ''
        profile_info = {}
        for trial_cnt in xrange(0, 3):
            profile_cmd_op, profile_err = tendrl_glusterfs_utils.exec_command(
                "gluster volume profile %s info --xml" % volName
            )
            if profile_err:
                time.sleep(5)
                if trial_cnt == 2:
                    collectd.error(
                        'Failed to fetch profile info. The error is: %s' % (
                            profile_err
                        )
                    )
                    return ret_val
                continue
            else:
                break
        try:
            profile_info = self._parseVolumeProfileInfo(
                ElementTree.fromstring(profile_cmd_op)
            )
            return profile_info
        except (
            AttributeError,
            KeyError,
            ValueError,
            ElementTree.ParseError
        ):
            collectd.error(
                'Failed to collect iops details of brick %s in volume %s of '
                'cluster %s. The profile info is %s. Error %s' % (
                    brickName,
                    volName,
                    cluster_id,
                    str(profile_info),
                    traceback.format_exc()
                )
            )
            return ret_val

    def process_volume_profile_info(self, volume):
        volName = volume['name']
        volId = volume['id']
        try:
            volData = self.etcd_client.read(
                '/clusters/%s/Volumes/%s/data' % (
                    self.CONFIG['integration_id'],
                    volId
                )
            ).value
            if not volData:
                return
            else:
                profiling_enabled = json.loads(volData).get(
                    'profiling_enabled'
                )
                if profiling_enabled and profiling_enabled != 'yes':
                    return
        except etcd.EtcdKeyNotFound:
            # Volume key not found return
            return

        vol_iops = self.get_volume_profile_info(
            volName,
            self.CONFIG['integration_id']
        )
        if not vol_iops:
            return
        read_write_hits = 0
        inode_hits = 0
        entry_hits = 0
        lock_hits = 0
        for brick_det in vol_iops.get('bricks', {}):
            brickName = brick_det.get('brick', '')
            brick_host = brick_det.get('brick', '').split(':')[0]
            brick_host = tendrl_glusterfs_utils.find_brick_host(
                self.etcd_client, self.CONFIG['integration_id'], brick_host
            )
            if not brick_host:
                continue

            if int(brick_det.get('intervalStats').get('duration')) > 0:
                # A sample output from command
                # `gluster v profile {vol} info --xml` is as below
                #
                # <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                # <cliOutput>
                #   <opRet>0</opRet>
                #   <opErrno>0</opErrno>
                #   <opErrstr/>
                #   <volProfile>
                #     <volname>vol1</volname>
                #     <profileOp>3</profileOp>
                #     <brickCount>3</brickCount>
                #     <brick>
                #       <brickName>
                #         dhcp42-80.lab.eng.blr.redhat.com:/root/gluster_bricks/vol1_b3
                #       </brickName>
                #       ...........
                #       <intervalStats>
                #         <blockStats>
                #           <block>
                #             <size>1</size>
                #             <reads>0</reads>
                #             <writes>512</writes>
                #           </block>
                #           <block>
                #             <size>2</size>
                #             <reads>0</reads>
                #             <writes>124</writes>
                #           </block>
                #           <block>
                #             <size>4</size>
                #             <reads>0</reads>
                #             <writes>100</writes>
                #           </block>
                #           .............
                #         </blockStats>
                #       </intervalStats>
                #     </brick>
                #   </volProfile>
                # </cliOutput>
                #
                # For calculating iops values we aggregate the reads
                # and writes across all blocks and then divide them with
                # `duration` value. These values are finally saved as
                # under `gauge_read` and `gauge_write` fields of graphite

                total_reads = 0
                for entry in brick_det.get('intervalStats').get('blockStats'):
                    total_reads += int(entry['read'])
                total_writes = 0
                for entry in brick_det.get('intervalStats').get('blockStats'):
                    total_writes += int(entry['write'])

                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s.iops." \
                    "gauge-read"
                self.profile_info[
                    t_name % (
                        self.CONFIG['integration_id'],
                        volName,
                        brick_host.replace('.', '_'),
                        brickName.split(':')[1].replace('/', self.brick_path_repl)
                    )
                ] = math.ceil(total_reads / float(
                    brick_det.get('intervalStats').get(
                        'duration'
                    )
                ))
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s.iops." \
                    "gauge-write"
                self.profile_info[
                    t_name % (
                        self.CONFIG['integration_id'],
                        volName,
                        brick_host.replace('.', '_'),
                        brickName.split(':')[1].replace('/', self.brick_path_repl)
                    )
                ] = math.ceil(total_writes / float(
                    brick_det.get('intervalStats').get(
                        'duration'
                    )
                ))
                t_name = "clusters.%s.nodes.%s.bricks.%s.iops." \
                    "gauge-read"
                self.profile_info[
                    t_name % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brickName.split(':')[1].replace('/', self.brick_path_repl)
                    )
                ] = math.ceil(total_reads / float(
                    brick_det.get('intervalStats').get(
                        'duration'
                    )
                ))
                t_name = "clusters.%s.nodes.%s.bricks.%s.iops." \
                    "gauge-write"
                self.profile_info[
                    t_name % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brickName.split(':')[1].replace('/', self.brick_path_repl)
                    )
                ] = math.ceil(total_writes / float(
                    brick_det.get('intervalStats').get(
                        'duration'
                    )
                ))
            fopIntervalStats = brick_det.get(
                'intervalStats'
            ).get('fopStats')
            for fopStat in fopIntervalStats:
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s.fop." \
                    "%s.hits"
                self.profile_info[
                    t_name % (
                        self.CONFIG['integration_id'],
                        volName,
                        brick_host.replace('.', '_'),
                        brickName.split(':')[1].replace('/', self.brick_path_repl),
                        fopStat.get('name')
                    )
                ] = float(fopStat.get('hits'))
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s.fop." \
                    "%s.latencyAvg"
                self.profile_info[
                    t_name % (
                        self.CONFIG['integration_id'],
                        volName,
                        brick_host.replace('.', '_'),
                        brickName.split(':')[1].replace('/', self.brick_path_repl),
                        fopStat.get('name')
                    )
                ] = float(fopStat.get('latencyAvg'))
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s.fop." \
                    "%s.latencyMin"
                self.profile_info[
                    t_name % (
                        self.CONFIG['integration_id'],
                        volName,
                        brick_host.replace('.', '_'),
                        brickName.split(':')[1].replace('/', self.brick_path_repl),
                        fopStat.get('name')
                    )
                ] = float(fopStat.get('latencyMin'))
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s.fop." \
                    "%s.latencyMax"
                self.profile_info[
                    t_name % (
                        self.CONFIG['integration_id'],
                        volName,
                        brick_host.replace('.', '_'),
                        brickName.split(':')[1].replace('/', self.brick_path_repl),
                        fopStat.get('name')
                    )
                ] = float(fopStat.get('latencyMax'))
                t_name = "clusters.%s.nodes.%s.bricks.%s.fop." \
                    "%s.hits"
                self.profile_info[
                    t_name % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brickName.split(':')[1].replace('/', self.brick_path_repl),
                        fopStat.get('name')
                    )
                ] = float(fopStat.get('hits'))
                t_name = "clusters.%s.nodes.%s.bricks.%s.fop." \
                    "%s.latencyAvg"
                self.profile_info[
                    t_name % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brickName.split(':')[1].replace('/', self.brick_path_repl),
                        fopStat.get('name')
                    )
                ] = float(fopStat.get('latencyAvg'))
                t_name = "clusters.%s.nodes.%s.bricks.%s.fop." \
                    "%s.latencyMin"
                self.profile_info[
                    t_name % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brickName.split(':')[1].replace('/', self.brick_path_repl),
                        fopStat.get('name')
                    )
                ] = float(fopStat.get('latencyMin'))
                t_name = "clusters.%s.nodes.%s.bricks.%s.fop." \
                    "%s.latencyMax"
                self.profile_info[
                    t_name % (
                        self.CONFIG['integration_id'],
                        brick_host.replace('.', '_'),
                        brickName.split(':')[1].replace('/', self.brick_path_repl),
                        fopStat.get('name')
                    )
                ] = float(fopStat.get('latencyMax'))
                if fopStat.get('name') in READ_WRITE_OPS:
                    read_write_hits = read_write_hits + float(
                        fopStat.get('hits')
                    )
                if fopStat.get('name') in LOCK_OPS:
                    lock_hits = lock_hits + float(fopStat.get('hits'))
                if fopStat.get('name') in INODE_OPS:
                    inode_hits = inode_hits + float(fopStat.get('hits'))
                if fopStat.get('name') in ENTRY_OPS:
                    entry_hits = entry_hits + float(fopStat.get('hits'))
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                "read_write_ops"
            self.profile_info[
                t_name % (
                    self.CONFIG['integration_id'],
                    volName,
                    brick_host.replace('.', '_'),
                    brickName.split(':')[1].replace('/', self.brick_path_repl)
                )
            ] = read_write_hits
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                "lock_ops"
            self.profile_info[
                t_name % (
                    self.CONFIG['integration_id'],
                    volName,
                    brick_host.replace('.', '_'),
                    brickName.split(':')[1].replace('/', self.brick_path_repl)
                )
            ] = lock_hits
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                "inode_ops"
            self.profile_info[
                t_name % (
                    self.CONFIG['integration_id'],
                    volName,
                    brick_host.replace('.', '_'),
                    brickName.split(':')[1].replace('/', self.brick_path_repl)
                )
            ] = inode_hits
            t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                "entry_ops"
            self.profile_info[
                t_name % (
                    self.CONFIG['integration_id'],
                    volName,
                    brick_host.replace('.', '_'),
                    brickName.split(':')[1].replace('/', self.brick_path_repl)
                )
            ] = entry_hits
            t_name = "clusters.%s.nodes.%s.bricks.%s." \
                "read_write_ops"
            self.profile_info[
                t_name % (
                    self.CONFIG['integration_id'],
                    brick_host.replace('.', '_'),
                    brickName.split(':')[1].replace('/', self.brick_path_repl)
                )
            ] = read_write_hits
            t_name = "clusters.%s.nodes.%s.bricks.%s." \
                "lock_ops"
            self.profile_info[
                t_name % (
                    self.CONFIG['integration_id'],
                    brick_host.replace('.', '_'),
                    brickName.split(':')[1].replace('/', self.brick_path_repl)
                )
            ] = lock_hits
            t_name = "clusters.%s.nodes.%s.bricks.%s." \
                "inode_ops"
            self.profile_info[
                t_name % (
                    self.CONFIG['integration_id'],
                    brick_host.replace('.', '_'),
                    brickName.split(':')[1].replace('/', self.brick_path_repl)
                )
            ] = inode_hits
            t_name = "clusters.%s.nodes.%s.bricks.%s." \
                "entry_ops"
            self.profile_info[
                t_name % (
                    self.CONFIG['integration_id'],
                    brick_host.replace('.', '_'),
                    brickName.split(':')[1].replace('/', self.brick_path_repl)
                )
            ] = entry_hits

    def get_volume_profile_metrics(self):
        global READ_WRITE_OPS
        global LOCK_OPS
        global INODE_OPS
        global ENTRY_OPS
        self.profile_info = {}
        volumes = self.CLUSTER_TOPOLOGY.get('volumes', [])
        # threads = []
        for volume in volumes:
            self.process_volume_profile_info(volume)
            # thread = threading.Thread(
            #    target=self.process_volume_profile_info,
            #    args=(volume,)
            # )
            # thread.start()
            # threads.append(thread)
        # for thread in threads:
        #    thread.join(1)
        # for thread in threads:
        #    del thread
        return self.profile_info

    def get_metrics(self):
        profile_info = {}
        heal_stats = {}
        profile_info = self.get_volume_profile_metrics()
        heal_stats = tendrl_gluster_heal_info.get_metrics(
            self.CLUSTER_TOPOLOGY,
            self.CONFIG,
            self.etcd_client,
            self.brick_path_repl
        )
        profile_info.update(heal_stats)
        return profile_info
