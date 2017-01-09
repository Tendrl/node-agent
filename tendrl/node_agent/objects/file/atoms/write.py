from tendrl.commons.atoms.base_atom import BaseAtom


class Write(BaseAtom):
    def run(self, parameters):
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
