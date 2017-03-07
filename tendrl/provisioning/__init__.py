from tendrl.commons import TendrlNS


class ProvisioningNS(TendrlNS):
    def __init__(self, ns_name="tendrl.provisioning",
                 ns_src="tendrl.provisioning"):
        super(ProvisioningNS, self).__init__(ns_name, ns_src)
