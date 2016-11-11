import os


class Check_node_up(object):
    def run(self, **kwargs):
        fqdn = kwargs.get("fqdn")
        response = os.system("ping -c 1 " + fqdn)
        # and then check the response...
        if response == 0:
            return True
        else:
            return False
