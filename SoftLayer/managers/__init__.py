"""
    SoftLayer.managers
    ~~~~~~~~~~~~~~~~~~
    Managers mask out a lot of the complexities of using the API into classes
    that provide a simpler interface to various services. These are
    higher-level interfaces to the SoftLayer API.

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.managers.cci import CCIManager
from SoftLayer.managers.dns import DNSManager
from SoftLayer.managers.firewall import FirewallManager
from SoftLayer.managers.hardware import HardwareManager
from SoftLayer.managers.image import ImageManager
from SoftLayer.managers.load_balancer import LoadBalancerManager
from SoftLayer.managers.messaging import MessagingManager
from SoftLayer.managers.metadata import MetadataManager
from SoftLayer.managers.network import NetworkManager
from SoftLayer.managers.sshkey import SshKeyManager
from SoftLayer.managers.ssl import SSLManager
from SoftLayer.managers.ticket import TicketManager

__all__ = ['CCIManager', 'DNSManager', 'FirewallManager', 'HardwareManager',
           'ImageManager', 'LoadBalancerManager', 'MessagingManager',
           'MetadataManager', 'NetworkManager', 'SshKeyManager', 'SSLManager',
           'TicketManager']
