"""
    SoftLayer Python API Client
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    SoftLayer API bindings

    Usage:

        >>> import SoftLayer
        >>> client = SoftLayer.Client(username="username", api_key="api_key")
        >>> resp = client['Account'].getObject()
        >>> resp['companyName']
        'Your Company'

    :license: MIT, see LICENSE for more details.
"""
# pylint: disable=w0401
from SoftLayer.consts import VERSION

from .API import *  # NOQA
from .managers import *  # NOQA
from .exceptions import *  # NOQA
from .auth import *  # NOQA

__title__ = 'SoftLayer'
__version__ = VERSION
__author__ = 'SoftLayer Technologies, Inc.'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014 SoftLayer Technologies, Inc.'
__all__ = ['Client', 'BasicAuthentication', 'SoftLayerError',
           'SoftLayerAPIError', 'API_PUBLIC_ENDPOINT', 'API_PRIVATE_ENDPOINT']
