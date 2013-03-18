__all__ = ["DedicatedManager"]


class DedicatedManager(object):
    """ Manages Dedicated Servers certificates. """

    def __init__(self, client):
        """ DedicatedManager initialization.

        :param SoftLayer.API.Client client: an API client instance

        """
        self.client = client
        self.dedicated = self.client['Hardware_Server']
        self.account = self.client['Account']

    def list_servers(self):
        """ List all certificates.

        :param method:  # TODO: explain this param

        """

        return self.account.getHardware()
