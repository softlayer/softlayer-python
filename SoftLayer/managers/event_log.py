"""
    SoftLayer.event_log
    ~~~~~~~~~~~~~~~~~~~
    Network Manager/helpers

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer import utils


class EventLogManager(object):
    """Provides an interface for the SoftLayer Event Log Service.

    See product information here:
    http://sldn.softlayer.com/reference/services/SoftLayer_Event_Log
    """

    def __init__(self, client):
        self.client = client
        self.event_log = client['Event_Log']

    def get_event_logs(self, request_filter=None, log_limit=20, iterator=True):
        """Returns a list of event logs

        Example::

            event_mgr = SoftLayer.EventLogManager(env.client)
            request_filter = event_mgr.build_filter(date_min="01/01/2019", date_max="02/01/2019")
            logs = event_mgr.get_event_logs(request_filter)
            for log in logs:
                print("Event Name: {}".format(log['eventName']))


        :param dict request_filter: filter dict
        :param int log_limit: number of results to get in one API call
        :param bool iterator: False will only make one API call for log_limit results.
            True will keep making API calls until all logs have been retreived. There may be a lot of these.
        :returns: List of event logs. If iterator=True, will return a python generator object instead.
        """
        if iterator:
            # Call iter_call directly as this returns the actual generator
            return self.client.iter_call('Event_Log', 'getAllObjects', filter=request_filter, limit=log_limit)
        return self.client.call('Event_Log', 'getAllObjects', filter=request_filter, limit=log_limit)

    def get_event_log_types(self):
        """Returns a list of event log types

        :returns: List of event log types
        """
        results = self.event_log.getAllEventObjectNames()
        return results

    @staticmethod
    def build_filter(date_min=None, date_max=None, obj_event=None, obj_id=None, obj_type=None, utc_offset=None):
        """Returns a query filter that can be passed into EventLogManager.get_event_logs

        :param string date_min: Lower bound date in MM/DD/YYYY format
        :param string date_max: Upper bound date in MM/DD/YYYY format
        :param string obj_event: The name of the events we want to filter by
        :param int obj_id: The id of the event we want to filter by
        :param string obj_type: The type of event we want to filter by
        :param string utc_offset: The UTC offset we want to use when converting date_min and date_max.
            (default '+0000')

        :returns: dict: The generated query filter
        """

        if not any([date_min, date_max, obj_event, obj_id, obj_type]):
            return {}

        request_filter = {}

        if date_min and date_max:
            request_filter['eventCreateDate'] = utils.event_log_filter_between_date(date_min, date_max, utc_offset)
        else:
            if date_min:
                request_filter['eventCreateDate'] = utils.event_log_filter_greater_than_date(date_min, utc_offset)
            elif date_max:
                request_filter['eventCreateDate'] = utils.event_log_filter_less_than_date(date_max, utc_offset)

        if obj_event:
            request_filter['eventName'] = {'operation': obj_event}

        if obj_id:
            request_filter['objectId'] = {'operation': obj_id}

        if obj_type:
            request_filter['objectName'] = {'operation': obj_type}

        return request_filter
