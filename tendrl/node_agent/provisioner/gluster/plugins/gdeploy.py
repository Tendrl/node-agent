import importlib

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
    from python_gdeploy.actions import remove_host
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
    def _reload_modules(self):
        globals()['install_gluster'] = importlib.import_module('python_gdeploy.actions.install_gluster')
        globals()['configure_gluster_service'] = importlib.import_module('python_gdeploy.actions.configure_gluster_service')
        globals()['configure_gluster_firewall'] = importlib.import_module('python_gdeploy.actions.configure_gluster_firewall')
        globals()['create_cluster'] = importlib.import_module('python_gdeploy.actions.create_cluster')
        globals()['remove_host'] = importlib.import_module('python_gdeploy.actions.remove_host')

    def setup_gluster_node(self, hosts, packages=None, repo=None):
        self._reload_modules()
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
        self._reload_modules()
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

    def expand_gluster_cluster(self, host):
        self._reload_modules()
        current_host = NS.node_context.fqdn
        out, err, rc = create_cluster.create_cluster(
            [current_host, host]
        )
        if rc == 0:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "gluster cluster expandeded successfully"
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
                        "message": "Error while expanding gluster cluster"
                        ". Details: %s" % str(out)
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
            return False
        return True

    def shrink_gluster_cluster(self, host):
        self._reload_modules()
        current_host = NS.node_context.fqdn
        out, err, rc = remove_host.remove_host(
            [current_host, host]
        )
        if rc == 0:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "gluster cluster shrinked successfully"
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
                        "message": "Error while shrinking gluster cluster"
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
