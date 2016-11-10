class Flow(object):
    def __init__(self, api_job):
        self.api_job = api_job

    def run(self):
        parameters = self.api_job['parameters']

        # Execute the pre runs for the flow
        for func in self.pre_run:
            mod_name = func[:func.rfind('.')]
            class_name = func[func.rfind('.') + 1:]
            ret_val = getattr(mod_name, class_name)(). \
                run(self.api_job['parameters'])
            if not ret_val:
                raise Exception(
                    "Error executing pre run function: %s" % func
                )

        # Execute the atoms for the flow
        for atom in self.atoms:
            mod_name = func[:func.rfind('.')]
            class_name = func[func.rfind('.') + 1:]
            ret_val = getattr(mod_name, class_name)(). \
                run(parameters)
            parameters.update(ret_val)

        # Execute the post runs for the flow
        for func in self.post_run:
            mod_name = func[:func.rfind('.')]
            class_name = func[func.rfind('.') + 1:]
            ret_val = getattr(mod_name, class_name)(). \
                run(self.api_job['parameters'])
            if not ret_val:
                raise Exception(
                    "Error executing post run function: %s" % func
                )
