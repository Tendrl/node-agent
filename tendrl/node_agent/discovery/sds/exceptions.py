class DiscoverSDSPluginNotImplementedError(NotImplementedError):
    def __init__(self, err):
        self.message = "discover_storage_system function not implemented. %s".\
            format(err)
