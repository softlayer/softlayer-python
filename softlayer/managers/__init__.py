"""
    softlayer.managers
    ~~~~~~~~~~~~~~~~~~
    Managers mask out a lot of the complexities of using the API into classes
    that provide a simpler interface to various services. These are
    higher-level interfaces to the SoftLayer api.

    :license: MIT, see LICENSE for more details.
"""
# pylint: disable=w0401

from softlayer.managers.cdn import CDNManager  # NOQA
from softlayer.managers.dns import DNSManager  # NOQA
from softlayer.managers.firewall import FirewallManager  # NOQA
from softlayer.managers.hardware import HardwareManager  # NOQA
from softlayer.managers.image import ImageManager  # NOQA
from softlayer.managers.iscsi import ISCSIManager  # NOQA
from softlayer.managers.load_balancer import LoadBalancerManager  # NOQA
from softlayer.managers.messaging import MessagingManager  # NOQA
from softlayer.managers.metadata import MetadataManager  # NOQA
from softlayer.managers.network import NetworkManager  # NOQA
from softlayer.managers.ordering import OrderingManager  # NOQA
from softlayer.managers.sshkey import SshKeyManager  # NOQA
from softlayer.managers.ssl import SSLManager  # NOQA
from softlayer.managers.ticket import TicketManager  # NOQA
from softlayer.managers.vs import VSManager  # NOQA

__all__ = ['DNSManager', 'FirewallManager', 'HardwareManager',
           'ImageManager', 'MessagingManager', 'MetadataManager', 'CDNManager',
           'NetworkManager', 'SshKeyManager', 'SSLManager', 'TicketManager',
           'VSManager', 'ISCSIManager', 'LoadBalancerManager',
           'OrderingManager']
