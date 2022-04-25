"""
    SoftLayer.transports.fixture
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Fixture transport, used for unit tests

    :license: MIT, see LICENSE for more details.
"""

import importlib


class FixtureTransport(object):
    """Implements a transport which returns fixtures."""

    def __call__(self, call):
        """Load fixture from the default fixture path."""
        try:
            module_path = 'SoftLayer.fixtures.%s' % call.service
            module = importlib.import_module(module_path)
        except ImportError as ex:
            message = '{} fixture is not implemented'.format(call.service)
            raise NotImplementedError(message) from ex
        try:
            return getattr(module, call.method)
        except AttributeError as ex:
            message = '{}::{} fixture is not implemented'.format(call.service, call.method)
            raise NotImplementedError(message) from ex

    @staticmethod
    def print_reproduceable(call):
        """Not Implemented"""
        return call.service
