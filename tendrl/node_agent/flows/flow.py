import logging

LOG = logging.getLogger(__name__)


class Flow(object):
    def __init__(self, job):
        self.job = job

    def run(self):
        parameters = self.job['parameters']
        parameters.update({'status': []})

        # Execute the pre runs for the flow
        LOG.info("Starting execution of pre-runs for flow: %s" %
                 self.job['flow'])
        for func in self.pre_run:
            mod_name = func[:func.rfind('.')]
            class_name = func[func.rfind('.') + 1:]
            ret_val = getattr(mod_name, class_name)(). \
                run(parameters)
            if not ret_val:
                LOG.error("Failed executing pre-run: %s for flow: %s" %
                          (func, self.job['flow']))
                raise Exception(
                    "Error executing pre run function: %s for flow: %s" %
                    (func, self.job['flow'])
                )
            else:
                LOG.info("Successfully executed pre-run: %s for flow: %s" %
                         (func, self.job['flow']))

        # Execute the atoms for the flow
        LOG.info("Starting execution of atoms for flow: %s" %
                 self.job['flow'])
        for atom in self.atoms:
            mod_name = func[:func.rfind('.')]
            class_name = func[func.rfind('.') + 1:]
            ret_val = getattr(mod_name, class_name)(). \
                run(parameters)
            if not ret_val:
                LOG.error("Failed executing atom: %s on flow: %s" %
                          (func, self.job['flow']))
                raise Exception(
                    "Error executing atom: %s on flow: %s" %
                    (atom, self.job['flow'])
                )
            else:
                LOG.info('Successfully executed atoms for flow: %s' %
                         self.job['flow'])

        # Execute the post runs for the flow
        LOG.info("Starting execution of post-runs for flow: %s" %
                 self.job['flow'])
        for func in self.post_run:
            mod_name = func[:func.rfind('.')]
            class_name = func[func.rfind('.') + 1:]
            ret_val = getattr(mod_name, class_name)(). \
                run(parameters)
            if not ret_val:
                LOG.error("Failed executing post-run: %s for flow: %s" %
                          (func, self.job['flow']))
                raise Exception(
                    "Error executing post run function: %s" % func
                )
            else:
                LOG.info("Successfully executed post-run: %s for flow: %s" %
                         (func, self.job['flow']))
