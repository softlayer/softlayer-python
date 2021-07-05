"""
    SoftLayer.managers
    ~~~~~~~~~~~~~~~~~~
    Managers mask out a lot of the complexities of using the API into classes
    that provide a simpler interface to various services. These are
    higher-level interfaces to the SoftLayer API.

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.managers.block import BlockStorageManager
from SoftLayer.managers.cdn import CDNManager
from SoftLayer.managers.dedicated_host import DedicatedHostManager
from SoftLayer.managers.dns import DNSManager
from SoftLayer.managers.event_log import EventLogManager
from SoftLayer.managers.file import FileStorageManager
from SoftLayer.managers.firewall import FirewallManager
from SoftLayer.managers.hardware import HardwareManager
from SoftLayer.managers.image import ImageManager
from SoftLayer.managers.ipsec import IPSECManager
from SoftLayer.managers.license import LicensesManager
from SoftLayer.managers.load_balancer import LoadBalancerManager
from SoftLayer.managers.metadata import MetadataManager
from SoftLayer.managers.network import NetworkManager
from SoftLayer.managers.object_storage import ObjectStorageManager
from SoftLayer.managers.ordering import OrderingManager
from SoftLayer.managers.sshkey import SshKeyManager
from SoftLayer.managers.ssl import SSLManager
from SoftLayer.managers.tags import TagManager
from SoftLayer.managers.ticket import TicketManager
from SoftLayer.managers.user import UserManager
from SoftLayer.managers.vs import VSManager
from SoftLayer.managers.vs_capacity import CapacityManager
from SoftLayer.managers.vs_placement import PlacementManager

__all__ = [
    'BlockStorageManager',
    'CapacityManager',
    'CDNManager',
    'DedicatedHostManager',
    'DNSManager',
    'EventLogManager',
    'FileStorageManager',
    'FirewallManager',
    'HardwareManager',
    'ImageManager',
    'IPSECManager',
    'LicensesManager',
    'LoadBalancerManager',
    'MetadataManager',
    'NetworkManager',
    'ObjectStorageManager',
    'OrderingManager',
    'PlacementManager',
    'SshKeyManager',
    'SSLManager',
    'TagManager',
    'TicketManager',
    'UserManager',
    'VSManager',
]
