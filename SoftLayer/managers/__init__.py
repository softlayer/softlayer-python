"""
    SoftLayer.managers
    ~~~~~~~~~~~~~~~~~~
    Managers mask out a lot of the complexities of using the API into classes
    that provide a simpler interface to various services. These are
    higher-level interfaces to the SoftLayer API.

    :license: MIT, see LICENSE for more details.
"""
# pylint: disable=w0401

from SoftLayer.managers.cci import CCIManager  # NOQA
from SoftLayer.managers.cdn import CDNManager  # NOQA
from SoftLayer.managers.dns import DNSManager  # NOQA
from SoftLayer.managers.firewall import FirewallManager  # NOQA
from SoftLayer.managers.hardware import HardwareManager  # NOQA
from SoftLayer.managers.image import ImageManager  # NOQA
from SoftLayer.managers.iscsi import ISCSIManager  # NOQA
from SoftLayer.managers.load_balancer import LoadBalancerManager  # NOQA
from SoftLayer.managers.messaging import MessagingManager  # NOQA
from SoftLayer.managers.metadata import MetadataManager  # NOQA
from SoftLayer.managers.network import NetworkManager  # NOQA
from SoftLayer.managers.ordering import OrderingManager  # NOQA
from SoftLayer.managers.sshkey import SshKeyManager  # NOQA
from SoftLayer.managers.ssl import SSLManager  # NOQA
from SoftLayer.managers.ticket import TicketManager  # NOQA
from SoftLayer.managers.vs import VSManager  # NOQA
from SoftLayer.managers.monitor import MonitoringManager # NOQA

__all__ = ['CCIManager', 'DNSManager', 'FirewallManager', 'HardwareManager',
           'ImageManager', 'MessagingManager', 'MetadataManager', 'CDNManager',
           'NetworkManager', 'SshKeyManager', 'SSLManager', 'TicketManager',
           'VSManager', 'ISCSIManager', 'LoadBalancerManager',
           'OrderingManager', 'MonitoringManager']
