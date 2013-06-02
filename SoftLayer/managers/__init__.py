"""
    SoftLayer.managers
    ~~~~~~~~~~~~~~~~~~
    Managers mask out a lot of the complexities of using the API into classes
    that provide a simpler interface to various services. These are
    higher-level interfaces to the SoftLayer API.

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from SoftLayer.managers.cci import CCIManager
from SoftLayer.managers.dns import DNSManager
from SoftLayer.managers.firewall import FirewallManager
from SoftLayer.managers.hardware import HardwareManager
from SoftLayer.managers.metadata import MetadataManager
from SoftLayer.managers.ssl import SSLManager

__all__ = ['CCIManager', 'DNSManager', 'FirewallManager', 'HardwareManager',
           'MetadataManager', 'SSLManager']
