class Generate(object):
    def run(self):
        data = "[gluster_bridge]\n# Path to log file\n"\
               "log_level = DEBUG\n" \
               "log_cfg_path = /etc/tendrl/gluster_bridge_logging.yaml"
        file_path = "/etc/tendrl/tendrl.conf"
        return {"data": data, "file_path": file_path}
