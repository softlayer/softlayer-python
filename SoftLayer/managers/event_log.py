"""
    SoftLayer.network
    ~~~~~~~~~~~~~~~~~
    Network Manager/helpers

    :license: MIT, see LICENSE for more details.
"""


class EventLogManager(object):
    """Provides an interface for the SoftLayer Event Log Service.

    See product information here:
    http://sldn.softlayer.com/reference/services/SoftLayer_Event_Log
    """
    def __init__(self, client):
        self.client = client

    def get_event_logs(self, request_filter):
        """Returns a list of event logs

        :param dict request_filter: filter dict
        :returns: List of event logs
        """
        results = self.client.call("Event_Log",
                                   'getAllObjects',
                                   filter=request_filter)
        return results
