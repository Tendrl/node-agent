from tendrl.commons.utils import ini2json

PATH = "tendrl/node_agent/tests/samples/gluster_state_sample.yaml"


class TendrlGlusterfsMonitoringBase(object):
    def __init__(self):
        self.CONFIG = dict(
            {
                "integration_id": "7bccda8c-8c85-45a8-8be0-3f71f4db7db7",
                "graphite_host": "localhost",
                "graphite_port": 8080,
                "peer_name": "10.70.41.169"
            }
        )


def gluster_state():
        return ini2json.ini_to_dict(PATH)
