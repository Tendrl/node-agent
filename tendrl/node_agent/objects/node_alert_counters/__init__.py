from tendrl.commons import objects


class NodeAlertCounters(objects.BaseObject):
    def __init__(
        self,
        warn_count=0,
        info_count=0,
        node_id='',
        *args,
        **kwargs
    ):
        super(NodeAlertCounters, self).__init__(*args, **kwargs)
        self.warning_count = warn_count
        self.info_count = info_count
        self.node_id = node_id
        self.value = '/nodes/{0}/alert_counters'

    def render(self):
        self.value = self.value.format(self.node_id)
        return super(NodeAlertCounters, self).render()
