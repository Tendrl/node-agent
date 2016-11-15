class Generate(object):
    def run(self, parameters):
        data = """\n[ceph_integration]\n# Path to log file\n\
               log_level = DEBUG\n \
               log_cfg_path = /etc/tendrl/ceph_integration_logging.yaml\n \
               crush_host_type = host\n
               crush_osd_type = osd\n
               favorite_timeout_factor = 3\n
               server_timeout_factor = 3\n
               cluster_contact_threshold = 60\n
               cluster_map_retention = 3600\n
               """
        file_path = "/etc/tendrl/tendrl.conf"
        parameters.update({"Config.data": data, "Config.file_path": file_path})
        return True
