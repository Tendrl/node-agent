import logging
from tendrl.node_agent.flows import utils

LOG = logging.getLogger(__name__)


class Flow(object):
    def __init__(self, flow_name, job, atoms, pre_run, post_run, uuid):
        self.job = job
        self.name = flow_name
        self.atoms = atoms
        self.pre_run = pre_run
        self.post_run = post_run
        self.uuid = uuid

    def run(self):
        post_atom = None
        pre_atom = None
        the_atom = None
        parameters = self.job['parameters']
        parameters.update({'log': []})

        # Execute the pre runs for the flow
        LOG.info("Starting execution of pre-runs for flow: %s" %
                 self.job['run'])
        for mod in self.pre_run:
            class_name = utils.to_camel_case(mod.split(".")[-1])
            if "tendrl" in mod and "atoms" in mod:
                exec("from %s import %s as pre_atom" % (mod,
                                                        class_name))

                ret_val = pre_atom().run(parameters)
            if not ret_val:
                LOG.error("Failed executing pre-run: %s for flow: %s" %
                          (pre_atom, self.job['run']))
                raise Exception(
                    "Error executing pre run function: %s for flow: %s" %
                    (pre_atom, self.job['run'])
                )
            else:
                LOG.info("Successfully executed pre-run: %s for flow: %s" %
                         (pre_atom, self.job['run']))

        # Execute the atoms for the flow
        LOG.info("Starting execution of atoms for flow: %s" %
                 self.job['run'])
        for atom in self.atoms:
            class_name = utils.to_camel_case(atom.split(".")[-1])
            if "tendrl" in atom and "atoms" in atom:
                exec("from %s import %s as the_atom" % (atom,
                                                        class_name))
                ret_val = the_atom().run(parameters)
            if not ret_val:
                LOG.error("Failed executing atom: %s on flow: %s" %
                          (the_atom, self.job['run']))
                raise Exception(
                    "Error executing atom: %s on flow: %s" %
                    (atom, self.job['run'])
                )
            else:
                LOG.info('Successfully executed atoms for flow: %s' %
                         self.job['run'])

        # Execute the post runs for the flow
        LOG.info("Starting execution of post-runs for flow: %s" %
                 self.job['run'])
        for mod in self.post_run:
            class_name = utils.to_camel_case(mod.split(".")[-1])
            if "tendrl" in atom and "atoms" in atom:
                exec("from %s import %s as post_atom" % (
                    mod,
                    class_name)
                )

                ret_val = post_atom().run(parameters)

            if not ret_val:
                LOG.error("Failed executing post-run: %s for flow: %s" %
                          (post_atom, self.job['run']))
                raise Exception(
                    "Error executing post run function: %s" % post_atom
                )
            else:
                LOG.info("Successfully executed post-run: %s for flow: %s" %
                         (post_atom, self.job['run']))
