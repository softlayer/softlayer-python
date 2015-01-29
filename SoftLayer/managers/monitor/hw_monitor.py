"""
    SoftLayer.monitor.hw_monitor
    ~~~~~~~~~~~~~~~~~~
    Monitoring Manager/helpers for Hardware_Server

    :license: MIT, see LICENSE for more details.
"""


class HardwareMonitorManager(object):
    """Manages monitoring for Hardware Servers

    :param SoftLayer.API.CLient client: an API client instance
    """

    def __init__(self, client):
        self.client = client
        self.account = self.client['Account']
        self.server = self.client['Hardware_Server']

    def list_status(self, **kwargs):
        """List all hardware with their monitoring status

        :param dict \\*\\*kwargs: response-level options (mask, limit, filter)
        :returns: Retrns a list of dictionaries with server and monitoring
                  information.
        """

        vs_items = [
            'id',
            'fullyQualifiedDomainName',
            'primaryBackendIpAddress',
            'primaryIpAddress',
            'datacenter',
            'networkMonitors[lastResult,queryType]'
        ]

        kwargs['mask'] = ('[mask[%s]]'
                          % (','.join(vs_items)))
        return self.account.call('getHardware', **kwargs)
