"""
    SoftLayer Python API Client
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    SoftLayer API bindings

    Usage:

        >>> import SoftLayer
        >>> client = SoftLayer.create_client_from_env(username="username",
                                                      api_key="api_key")
        >>> resp = client['Account'].getObject()
        >>> resp['companyName']
        'Your Company'

    :license: MIT, see LICENSE for more details.
"""
# pylint: disable=w0401
from SoftLayer import consts

from SoftLayer.API import *  # NOQA
from SoftLayer.managers import *  # NOQA
from SoftLayer.exceptions import *  # NOQA
from SoftLayer.auth import *  # NOQA
from SoftLayer.transports import *  # NOQA

__title__ = 'SoftLayer'
__version__ = consts.VERSION
__author__ = 'SoftLayer Technologies, Inc.'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014 SoftLayer Technologies, Inc.'
__all__ = ['BaseClient', 'create_client_from_env', 'Client',
           'BasicAuthentication', 'SoftLayerError', 'SoftLayerAPIError',
           'API_PUBLIC_ENDPOINT', 'API_PRIVATE_ENDPOINT']
