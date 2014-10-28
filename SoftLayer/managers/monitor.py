"""
    SoftLayer.monitor
    ~~~~~~~~~~~~~~~~~~
    Monitoring Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
# Invalid names are ignored due to long method names and short argument names
# pylint: disable=C0103

from SoftLayer import utils


class MonitoringManager(utils.IdentifierMixin, object):
    """
    Manages monitoring for Hardware and Virtual Servers

    :param SoftLayer.API.CLient client: an API client instance
    :param string server_tpe: should be either
                  'Hardware_Server' or 'Virtual_Guest'

    """

    def __init__(self, client, server_type='Hardware_Server'):
        self.client = client
        self.account = self.client['Account']
        self.server = self.client[server_type]

    def get_status(self, server_id):
        """ get the monitoring status of a server
        :param int server_id: the id of the server

        Definition of some of the monitoring status codes
         0 = Down
         1 = Warning
         2 = OK
         >2 = something strange happened
        """

        mask = "lastResult, subnet[virtualGuests,hardware]"
        agent = self.server.getNetworkMonitors(id=server_id, mask=mask)
        return agent

    def list_hardware_status(self, **kwargs):
        """ List all hardware with their monitoring status

        :param dict \\*\\*kwargs: response-level options (mask, limit, filter)
        :returns: Retrns a list of dictionaries with server and monitoring
                  information.
        """
        if 'mask' not in kwargs:
            hw_items = [
                'id',
                'fullyQualifiedDomainName',
                'primaryBackendIpAddress',
                'primaryIpAddress',
                'datacenter',
                'networkMonitors[lastResult]'
            ]

            kwargs['mask'] = ('[mask[%s]]'
                              % (','.join(hw_items)))
        kwargs['filter'] = ''
        output = self.account.getHardware(**kwargs)
        return output
