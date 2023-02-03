"""
    SoftLayer.transports
    ~~~~~~~~~~~~~~~~~~~~
    XML-RPC transport layer that uses the requests library.

    :license: MIT, see LICENSE for more details.
"""
# Required imports to not break existing code.


from .debug import DebugTransport
from .fixture import FixtureTransport
from .rest import RestTransport
from .timing import TimingTransport
from .transport import Request
from .transport import SoftLayerListResult as SoftLayerListResult
from .xmlrpc import XmlRpcTransport

# transports.Request does have a lot of instance attributes. :(
# pylint: disable=too-many-instance-attributes

__all__ = [
    'Request',
    'XmlRpcTransport',
    'RestTransport',
    'TimingTransport',
    'DebugTransport',
    'FixtureTransport',
    'SoftLayerListResult'
]
