from tendrl.commons import TendrlNS


class CephIntegrationNS(TendrlNS):
    def __init__(self, ns_name="tendrl.integrations.ceph",
                 ns_src="tendrl.integrations.ceph"):
        super(CephIntegrationNS, self).__init__(ns_name, ns_src)
