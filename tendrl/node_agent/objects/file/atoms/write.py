from tendrl.commons.objects import atoms

from tendrl.node_agent.objects import file


class Write(atoms.BaseAtom):
    obj = file.File

    def run(self, parameters=None, *args, **kwargs):
        super(Write, self).run(*args, **kwargs)
        data = parameters.get("Config.data")
        file_path = parameters.get("Config.file_path")
        attributes = {}
        attributes["block"] = data
        attributes["dest"] = file_path
        try:
            with open(file_path, 'a+') as f:
                f.write(data)
        except Exception as e:
            raise e
        return True
