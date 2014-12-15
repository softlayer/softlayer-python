"""
    SoftLayer Python API Client
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    SoftLayer API bindings

    Usage:

        >>> import softlayer
        >>> client = softlayer.Client(username="username", api_key="api_key")
        >>> resp = client['Account'].getObject()
        >>> resp['companyName']
        'Your Company'

    :license: MIT, see LICENSE for more details.
"""
# pylint: disable=w0401
from softlayer import consts

from softlayer.api import *  # NOQA
from softlayer.managers import *  # NOQA
from softlayer.exceptions import *  # NOQA
from softlayer.auth import *  # NOQA
from softlayer.transports import *  # NOQA

__title__ = 'softlayer'
__version__ = consts.VERSION
__author__ = 'SoftLayer Technologies, Inc.'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014 SoftLayer Technologies, Inc.'
__all__ = ['Client', 'BasicAuthentication', 'SoftLayerError',
           'SoftLayerAPIError', 'API_PUBLIC_ENDPOINT', 'API_PRIVATE_ENDPOINT']
