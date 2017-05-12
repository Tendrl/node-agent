from tendrl.commons import objects


class Journal(objects.BaseObject):
    internal = True
    def __init__(self, integration_id, node_id, data, *args, **kwargs):
        self._defs = {}
        super(Journal, self).__init__(*args, **kwargs)

        self.integration_id = integration_id
        self.node_id = node_id
        self.data = data
        self.value = "clusters/%s/JournalDetails/%s"

    def render(self):
        self.__name__ = self.__name__ % (
            self.integration_id,
            self.node_id
        )
        return super(_Journal, self).render()
