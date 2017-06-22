from tendrl.commons import objects


class Journal(objects.BaseObject):
    internal = True

    def __init__(self, integration_id=None, node_id=None, data=None, *args,
                 **kwargs):
        self._defs = {}
        super(Journal, self).__init__(*args, **kwargs)

        self.integration_id = integration_id
        self.node_id = node_id
        self.data = data
        self.value = "clusters/{0}/JournalDetails/{1}"

    def render(self):
        self.value = self.value.format(self.integration_id, self.node_id)
        return super(Journal, self).render()
