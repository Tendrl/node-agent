from tendrl.commons.utils \
    import service

TENDRL_CLUSTER_ID_PATH_PREFIX = "/var/lib/tendrl/"


class StartIntegrationService(object):
    def run(self, parameters):
        # write the cluster_id to cluster_id file
        cluster_id_path = TENDRL_CLUSTER_ID_PATH_PREFIX + parameters.get(
            "Tendrl_context.sds_name") + "_cluster_id"
        try:
            with open(cluster_id_path, "w") as f:
                f.write(parameters.get("Tendrl_context.cluster_id"))
        except IOError:
            # TODO(darshan) log here
            return False

        # start service
        service_name = "tendrl-" + parameters.get(
            "Tendrl_context.sds_name") + "d"
        s = service.Service(service_name)
        message, success = s.start()
        # TODO(darshan) log here
        return success
