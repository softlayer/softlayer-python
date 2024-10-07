"""
    SoftLayer.transports.fixture
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Fixture transport, used for unit tests

    :license: MIT, see LICENSE for more details.
"""

import importlib

from .transport import SoftLayerListResult


class FixtureTransport(object):
    """Implements a transport which returns fixtures."""

    def __call__(self, call):
        """Load fixture from the default fixture path."""
        try:
            module_path = 'SoftLayer.fixtures.%s' % call.service
            module = importlib.import_module(module_path)
        except ImportError as ex:
            message = f'{call.service} fixture is not implemented'
            raise NotImplementedError(message) from ex
        try:
            result = getattr(module, call.method)
            if isinstance(result, list):
                return SoftLayerListResult(result, len(result))
            return result
        except AttributeError as ex:
            message = f'{call.service}::{call.method} fixture is not implemented'
            raise NotImplementedError(message) from ex

    @staticmethod
    def print_reproduceable(call):
        """Not Implemented"""
        return call.service
