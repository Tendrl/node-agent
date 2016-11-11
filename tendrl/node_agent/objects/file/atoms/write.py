class Write(object):
    def run(self, **kwargs):
        data = kwargs.get("data")
        file_path = kwargs.get("file_path")
        attributes = {}
        attributes["block"] = data
        attributes["dest"] = file_path
        try:
            with open(file_path, 'a+') as f:
                f.write(data)
        except Exception as e:
            raise e
        return {}
