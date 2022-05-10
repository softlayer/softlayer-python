"""
    SoftLayer.transports.timing
    ~~~~~~~~~~~~~~~~~~~~
    Timing transport, used when you want to know how long an API call took.

    :license: MIT, see LICENSE for more details.
"""
import time


class TimingTransport(object):
    """Transport that records API call timings."""

    def __init__(self, transport):
        self.transport = transport
        self.last_calls = []

    def __call__(self, call):
        """See Client.call for documentation."""
        start_time = time.time()

        result = self.transport(call)

        end_time = time.time()
        self.last_calls.append((call, start_time, end_time - start_time))
        return result

    def get_last_calls(self):
        """Retrieves the last_calls property.

        This property will contain a list of tuples in the form
        (Request, initiated_utc_timestamp, execution_time)
        """
        last_calls = self.last_calls
        self.last_calls = []
        return last_calls

    @staticmethod
    def print_reproduceable(call):
        """Not Implemented"""
        return call.service
