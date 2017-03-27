from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.utils.ssh import generate_key
from tendrl.node_agent.provisioner.gluster.provisioner_base import\
    ProvisionerBasePlugin

try:
    from python_gdeploy.actions import install_gluster
    from python_gdeploy.actions import configure_gluster_service
    from python_gdeploy.actions import configure_gluster_firewall
    from python_gdeploy.actions import create_cluster
except ImportError:
    Event(
        Message(
            priority="info",
            publisher=NS.publisher_id,
            payload={
                "message": "python-gdeploy is not installed in this node"
            },
            cluster_id=NS.tendrl_context.integration_id,
        )
    )


class GdeployPlugin(ProvisionerBasePlugin):
    def setup_gluster_node(self, hosts, packages=None, repo=None):
        out, err, rc = install_gluster.install_gluster_packages(
            hosts,
            packages,
            repo
        )
        if rc == 0:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "gluster packages installed successfully"
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
        else:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Error while installing glusterfs packages"
                        ". Details: %s" % str(out)
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
            return False

        out, err, rc = configure_gluster_service.configure_gluster_service(
            hosts
        )
        if rc == 0:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "glusterd service started successfully"
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
        else:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Error while starting glusterd service"
                        ". Details: %s" % str(out)
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
            return False

        out, err, rc = configure_gluster_firewall.configure_gluster_firewall(
            hosts
        )
        if rc == 0:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "gluster firewall configured successfully"
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
        else:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Error while configuring gluster firewall"
                        ". Details: %s" % str(out)
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
            return False
        return True

    def create_gluster_cluster(self, hosts):
        out, err, rc = create_cluster.create_cluster(
            hosts
        )
        if rc == 0:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "gluster cluster created successfully"
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
        else:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Error while creating gluster cluster"
                        ". Details: %s" % str(out)
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
            return False
        return True

    def setup(self):
        result, err = generate_key.GenerateKey().run()
        return result, err
