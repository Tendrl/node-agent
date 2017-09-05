from tendrl.commons import objects


class ClusterAlertCounters(objects.BaseObject):
    def __init__(
        self,
        warn_count=0,
        integration_id='',
        *args,
        **kwargs
    ):
        super(ClusterAlertCounters, self).__init__(*args, **kwargs)
        self.warning_count = warn_count
        self.integration_id = integration_id
        self.value = '/clusters/{0}/alert_counters'

    def render(self):
        self.value = self.value.format(self.integration_id)
        return super(ClusterAlertCounters, self).render()
