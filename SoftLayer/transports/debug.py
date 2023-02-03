"""
    SoftLayer.transports.debug
    ~~~~~~~~~~~~~~~~~~~~
    Debugging transport. Will print out verbose logging information.

    :license: MIT, see LICENSE for more details.
"""

import json
import logging
import time

from SoftLayer import exceptions


class DebugTransport(object):
    """Transport that records API call timings."""

    def __init__(self, transport):
        self.transport = transport

        #: List All API calls made during a session
        self.requests = []
        self.logger = logging.getLogger(__name__)

    def __call__(self, call):
        call.start_time = time.time()

        self.pre_transport_log(call)
        try:
            call.result = self.transport(call)
        except (exceptions.SoftLayerAPIError, exceptions.TransportError) as ex:
            call.exception = ex

        self.post_transport_log(call)

        call.end_time = time.time()
        self.requests.append(call)

        if call.exception is not None:
            self.logger.debug(self.print_reproduceable(call))
            raise call.exception

        return call.result

    def pre_transport_log(self, call):
        """Prints a warning before calling the API """
        output = "Calling: {})".format(call)
        self.logger.warning(output)

    def post_transport_log(self, call):
        """Prints the result "Returned Data: \n%s" % (call.result)of an API call"""
        output = "Returned Data: \n{}".format(json.dumps(call.result))
        self.logger.debug(output)

    def get_last_calls(self):
        """Returns all API calls for a session"""
        return self.requests

    def print_reproduceable(self, call):
        """Prints a reproduceable debugging output"""
        return self.transport.print_reproduceable(call)
