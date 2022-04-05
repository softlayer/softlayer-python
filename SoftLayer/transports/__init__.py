"""
    SoftLayer.transports
    ~~~~~~~~~~~~~~~~~~~~
    XML-RPC transport layer that uses the requests library.

    :license: MIT, see LICENSE for more details.
"""


import requests


# Required imports to not break existing code.
from .rest import RestTransport
from .xmlrpc import XmlRpcTransport
from .fixture import FixtureTransport
from .timing import TimingTransport
from .debug import DebugTransport

from .transport import Request
from .transport import SoftLayerListResult as SoftLayerListResult


# transports.Request does have a lot of instance attributes. :(
# pylint: disable=too-many-instance-attributes, no-self-use

__all__ = [
    'Request',
    'XmlRpcTransport',
    'RestTransport',
    'TimingTransport',
    'DebugTransport',
    'FixtureTransport',
    'SoftLayerListResult'
]










