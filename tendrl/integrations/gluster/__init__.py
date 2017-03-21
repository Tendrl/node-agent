from tendrl.commons import TendrlNS


class GlusterIntegrationNS(TendrlNS):
    def __init__(self, ns_name="integrations.gluster",
                 ns_src="tendrl.integrations.gluster"):
        super(GlusterIntegrationNS, self).__init__(ns_name, ns_src)
