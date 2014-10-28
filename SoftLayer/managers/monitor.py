"""
    SoftLayer.monitor
    ~~~~~~~~~~~~~~~~~~
    Monitoring Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
# Invalid names are ignored due to long method names and short argument names
# pylint: disable=C0103
import socket

from SoftLayer.managers import ordering
from SoftLayer.managers import hardware
from SoftLayer.managers import vs
from SoftLayer import utils

from pprint import pprint as pp

class MonitoringManager(utils.IdentifierMixin, object):
    """
    Manages monitoring for Hardware and Virtual Servers

    :param SoftLayer.API.CLient client: an API client instance
    :param string server_tpe: should be either 
                  'Hardware_Server' or 'Virtual_Guest'

    """

    def __init__(self, client, server_type = 'Hardware_Server'):
        self.client = client
        self.account = self.client['Account']
        # self.resolvers = [self._get_ids_from_ip, self._get_ids_from_hostname]
        self.server = self.client[server_type]


    def get_status(self, server_id):
        #Monitoring Status number meanings
        # 0 = Down
        # 1 = Warning
        # 2 = OK
        # >2 = something strange happened

        print "\033[32mGetting status of %s\033[0m" % server_id
        mask = "lastResult, subnet[virtualGuests,hardware]"
        agent = self.server.getNetworkMonitors(id=server_id, mask=mask)
        pp(agent)

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

