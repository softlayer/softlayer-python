"""
    SoftLayer.event_log
    ~~~~~~~~~~~~~~~~~
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
        self.event_log = client['Event_Log']

    def get_event_logs(self, request_filter):
        """Returns a list of event logs

        :param dict request_filter: filter dict
        :returns: List of event logs
        """
        results = self.event_log.getAllObjects(filter=request_filter)
        return results

    def get_event_log_types(self):
        """Returns a list of event log types

        :returns: List of event log types
        """
        results = self.event_log.getAllEventObjectNames()
        return results

    def get_event_logs_by_type(self, event_type):
        """Returns a list of event logs, filtered on the 'objectName' field

        :param string event_type: The event type we want to filter on
        :returns: List of event logs, filtered on the 'objectName' field
        """
        request_filter = {}
        request_filter['objectName'] = {'operation': event_type}

        return self.event_log.getAllObjects(filter=request_filter)

    def get_event_logs_by_event_name(self, event_name):
        """Returns a list of event logs, filtered on the 'eventName' field

        :param string event_type: The event type we want to filter on
        :returns: List of event logs, filtered on the 'eventName' field
        """
        request_filter = {}
        request_filter['eventName'] = {'operation': event_name}

        return self.event_log.getAllObjects(filter=request_filter)

    @staticmethod
    def build_filter(date_min, date_max, obj_event, obj_id, obj_type, utc_offset):
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

        if not date_min and not date_max and not obj_event and not obj_id and not obj_type:
            return None

        request_filter = {}

        if date_min and date_max:
            request_filter['eventCreateDate'] = utils.event_log_filter_between_date(date_min, date_max, utc_offset)
        else:
            if date_min:
                request_filter['eventCreateDate'] = utils.event_log_filter_greater_than_date(
                    date_min,
                    utc_offset
                )
            elif date_max:
                request_filter['eventCreateDate'] = utils.event_log_filter_less_than_date(
                    date_max,
                    utc_offset
                )

        if obj_event:
            request_filter['eventName'] = {'operation': obj_event}

        if obj_id:
            request_filter['objectId'] = {'operation': obj_id}

        if obj_type:
            request_filter['objectName'] = {'operation': obj_type}

        return request_filter
