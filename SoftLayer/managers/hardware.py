"""
    SoftLayer.hardware
    ~~~~~~~~~~~~~~~~~~
    Hardware Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
import socket

import SoftLayer
from SoftLayer.managers import ordering
from SoftLayer import utils
# Invalid names are ignored due to long method names and short argument names
# pylint: disable=invalid-name, no-self-use

EXTRA_CATEGORIES = ['pri_ipv6_addresses',
                    'static_ipv6_addresses',
                    'sec_ip_addresses']


class HardwareManager(utils.IdentifierMixin, object):
    """Manage hardware devices.

    :param SoftLayer.API.Client client: an API client instance
    :param SoftLayer.managers.OrderingManager ordering_manager: an optional
                                              manager to handle ordering.
                                              If none is provided, one will be
                                              auto initialized.
    """
    def __init__(self, client, ordering_manager=None):
        self.client = client
        self.hardware = self.client['Hardware_Server']
        self.account = self.client['Account']
        self.resolvers = [self._get_ids_from_ip, self._get_ids_from_hostname]
        if ordering_manager is None:
            self.ordering_manager = ordering.OrderingManager(client)
        else:
            self.ordering_manager = ordering_manager

    def cancel_hardware(self, hardware_id, reason='unneeded', comment='',
                        immediate=False):
        """Cancels the specified dedicated server.

        :param int hardware_id: The ID of the hardware to be cancelled.
        :param string reason: The reason code for the cancellation. This should
                              come from :func:`get_cancellation_reasons`.
        :param string comment: An optional comment to include with the
                               cancellation.
        """

        # Get cancel reason
        reasons = self.get_cancellation_reasons()
        cancel_reason = reasons.get(reason, reasons['unneeded'])

        hw_billing = self.get_hardware(hardware_id,
                                       mask='mask[id, billingItem.id]')
        if 'billingItem' not in hw_billing:
            raise SoftLayer.SoftLayerError(
                "No billing item found for hardware")

        billing_id = hw_billing['billingItem']['id']

        return self.client.call('Billing_Item', 'cancelItem',
                                immediate, False, cancel_reason, comment,
                                id=billing_id)

    def list_hardware(self, tags=None, cpus=None, memory=None, hostname=None,
                      domain=None, datacenter=None, nic_speed=None,
                      public_ip=None, private_ip=None, **kwargs):
        """List all hardware (servers and bare metal computing instances).

        :param list tags: filter based on tags
        :param integer cpus: filter based on number of CPUS
        :param integer memory: filter based on amount of memory in gigabytes
        :param string hostname: filter based on hostname
        :param string domain: filter based on domain
        :param string datacenter: filter based on datacenter
        :param integer nic_speed: filter based on network speed (in MBPS)
        :param string public_ip: filter based on public ip address
        :param string private_ip: filter based on private ip address
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        :returns: Returns a list of dictionaries representing the matching
                  hardware. This list will contain both dedicated servers and
                  bare metal computing instances

        """
        if 'mask' not in kwargs:
            hw_items = [
                'id',
                'hostname',
                'domain',
                'hardwareStatusId',
                'globalIdentifier',
                'fullyQualifiedDomainName',
                'processorPhysicalCoreAmount',
                'memoryCapacity',
                'primaryBackendIpAddress',
                'primaryIpAddress',
                'datacenter',
            ]
            server_items = [
                'activeTransaction[id, transactionStatus[friendlyName,name]]',
            ]

            kwargs['mask'] = ('[mask[%s],'
                              ' mask(SoftLayer_Hardware_Server)[%s]]'
                              % (','.join(hw_items), ','.join(server_items)))

        _filter = utils.NestedDict(kwargs.get('filter') or {})
        if tags:
            _filter['hardware']['tagReferences']['tag']['name'] = {
                'operation': 'in',
                'options': [{'name': 'data', 'value': tags}],
            }

        if cpus:
            _filter['hardware']['processorPhysicalCoreAmount'] = (
                utils.query_filter(cpus))

        if memory:
            _filter['hardware']['memoryCapacity'] = utils.query_filter(memory)

        if hostname:
            _filter['hardware']['hostname'] = utils.query_filter(hostname)

        if domain:
            _filter['hardware']['domain'] = utils.query_filter(domain)

        if datacenter:
            _filter['hardware']['datacenter']['name'] = (
                utils.query_filter(datacenter))

        if nic_speed:
            _filter['hardware']['networkComponents']['maxSpeed'] = (
                utils.query_filter(nic_speed))

        if public_ip:
            _filter['hardware']['primaryIpAddress'] = (
                utils.query_filter(public_ip))

        if private_ip:
            _filter['hardware']['primaryBackendIpAddress'] = (
                utils.query_filter(private_ip))

        kwargs['filter'] = _filter.to_dict()
        return self.account.getHardware(**kwargs)

    def get_hardware(self, hardware_id, **kwargs):
        """Get details about a hardware device.

        :param integer id: the hardware ID
        :returns: A dictionary containing a large amount of information about
                  the specified server.

        """

        if 'mask' not in kwargs:
            items = [
                'id',
                'globalIdentifier',
                'fullyQualifiedDomainName',
                'hostname',
                'domain',
                'provisionDate',
                'hardwareStatus',
                'processorPhysicalCoreAmount',
                'memoryCapacity',
                'notes',
                'privateNetworkOnlyFlag',
                'primaryBackendIpAddress',
                'primaryIpAddress',
                'networkManagementIpAddress',
                'userData',
                'datacenter',
                '''networkComponents[id, status, speed, maxSpeed, name,
                   ipmiMacAddress, ipmiIpAddress, macAddress, primaryIpAddress,
                   port, primarySubnet[id, netmask, broadcastAddress,
                                       networkIdentifier, gateway]]''',
                'hardwareChassis[id,name]',
                'activeTransaction[id, transactionStatus[friendlyName,name]]',
                '''operatingSystem[
                    softwareLicense[softwareDescription[manufacturer,
                                                        name,
                                                        version,
                                                        referenceCode]],
                    passwords[username,password]]''',
                'billingItem.nextInvoiceTotalRecurringAmount',
                'hourlyBillingFlag',
                'tagReferences[id,tag[name,id]]',
                'networkVlans[id,vlanNumber,networkSpace]',
                'billingItem.orderItem.order.userRecord[username]',
                'remoteManagementAccounts[username,password]',
            ]
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        return self.hardware.getObject(id=hardware_id, **kwargs)

    def reload(self, hardware_id, post_uri=None, ssh_keys=None):
        """Perform an OS reload of a server with its current configuration.

        :param integer hardware_id: the instance ID to reload
        :param string post_url: The URI of the post-install script to run
                                after reload
        :param list ssh_keys: The SSH keys to add to the root user
        """

        config = {}

        if post_uri:
            config['customProvisionScriptUri'] = post_uri

        if ssh_keys:
            config['sshKeyIds'] = [key_id for key_id in ssh_keys]

        return self.hardware.reloadOperatingSystem('FORCE', config,
                                                   id=hardware_id)

    def rescue(self, hardware_id):
        """Reboot a server into the a recsue kernel.

        :param integer instance_id: the server ID to rescue
        """
        return self.hardware.bootToRescueLayer(id=hardware_id)

    def change_port_speed(self, hardware_id, public, speed):
        """Allows you to change the port speed of a server's NICs.

        :param int hardware_id: The ID of the server
        :param bool public: Flag to indicate which interface to change.
                            True (default) means the public interface.
                            False indicates the private interface.
        :param int speed: The port speed to set.
        """
        if public:
            func = self.hardware.setPublicNetworkInterfaceSpeed
        else:
            func = self.hardware.setPrivateNetworkInterfaceSpeed

        return func(speed, id=hardware_id)

    def place_order(self, **kwargs):
        """Places an order for a piece of hardware.

        See get_create_options() for valid arguments.

        :param string size: server size name
        :param string hostname: server hostname
        :param string domain: server domain name
        :param string location: location (datacenter) name
        :param string os: operating system name
        :param int port_speed: Port speed in Mbps
        :param list ssh_keys: list of ssh key ids
        :param int public_vlan: public vlan id
        :param int private_vlan: private vlan id
        :param string post_uri: The URI of the post-install script to run
                                after reload
        :param boolean hourly: True if using hourly pricing (default).
                               False for monthly.
        :param boolean no_public: True if this server should only have private
                                  interfaces
        :param list extras: List of extra feature names
        """
        create_options = self._generate_create_dict(**kwargs)
        return self.client['Product_Order'].placeOrder(create_options)

    def verify_order(self, **kwargs):
        """Verifies an order for a piece of hardware.

        See :func:`place_order` for a list of available options.
        """
        create_options = self._generate_create_dict(**kwargs)
        return self.client['Product_Order'].verifyOrder(create_options)

    def get_cancellation_reasons(self):
        """Returns a dictionary of valid cancellation reasons.

        These can be used when cancelling a dedicated server
        via :func:`cancel_hardware`.
        """
        return {
            'unneeded': 'No longer needed',
            'closing': 'Business closing down',
            'cost': 'Server / Upgrade Costs',
            'migrate_larger': 'Migrating to larger server',
            'migrate_smaller': 'Migrating to smaller server',
            'datacenter': 'Migrating to a different SoftLayer datacenter',
            'performance': 'Network performance / latency',
            'support': 'Support response / timing',
            'sales': 'Sales process / upgrades',
            'moving': 'Moving to competitor',
        }

    def get_create_options(self):
        """Returns valid options for ordering hardware."""

        package = self._get_package()

        # Locations
        locations = []
        for region in package['regions']:
            locations.append({
                'name': region['location']['location']['longName'],
                'key': region['location']['location']['name'],
            })

        # Sizes
        sizes = []
        for preset in package['activePresets']:
            sizes.append({
                'name': preset['description'],
                'key': preset['keyName']
            })

        # Operating systems
        operating_systems = []
        for item in package['items']:
            if item['itemCategory']['categoryCode'] == 'os':
                operating_systems.append({
                    'name': item['softwareDescription']['longDescription'],
                    'key': item['softwareDescription']['referenceCode'],
                })

        # Port speeds
        port_speeds = []
        for item in package['items']:
            if all([item['itemCategory']['categoryCode'] == 'port_speed',
                    not _is_private_port_speed_item(item)]):
                port_speeds.append({
                    'name': item['description'],
                    'key': item['capacity'],
                })

        # Extras
        extras = []
        for item in package['items']:
            if item['itemCategory']['categoryCode'] in EXTRA_CATEGORIES:
                extras.append({
                    'name': item['description'],
                    'key': item['keyName']
                })

        return {
            'locations': locations,
            'sizes': sizes,
            'operating_systems': operating_systems,
            'port_speeds': port_speeds,
            'extras': extras,
        }

    def _get_package(self):
        """Get the package related to simple hardware ordering."""
        mask = '''
items[
    keyName,
    capacity,
    description,
    attributes[id,attributeTypeKeyName],
    itemCategory[id,categoryCode],
    softwareDescription[id,referenceCode,longDescription],
    prices
],
activePresets,
regions[location[location]]
'''

        package_type = 'BARE_METAL_CPU_FAST_PROVISION'
        packages = self.ordering_manager.get_packages_of_type([package_type],
                                                              mask=mask)
        if len(packages) != 1:
            raise SoftLayer.SoftLayerError("Ordering package not found")

        return packages[0]

    def _generate_create_dict(self,
                              size=None,
                              hostname=None,
                              domain=None,
                              location=None,
                              os=None,
                              port_speed=None,
                              ssh_keys=None,
                              public_vlan=None,
                              private_vlan=None,
                              post_uri=None,
                              hourly=True,
                              no_public=False,
                              extras=None):
        """Translates arguments into a dictionary for creating a server."""

        extras = extras or []

        package = self._get_package()

        prices = []
        for category in ['pri_ip_addresses',
                         'vpn_management',
                         'remote_management']:
            prices.append(_get_default_price_id(package['items'],
                                                category,
                                                hourly))

        prices.append(_get_os_price_id(package['items'], os))
        prices.append(_get_bandwidth_price_id(package['items'],
                                              hourly=hourly,
                                              no_public=no_public))
        prices.append(_get_port_speed_price_id(package['items'],
                                               port_speed,
                                               no_public))

        for extra in extras:
            prices.append(_get_extra_price_id(package['items'], extra, hourly))

        hardware = {
            'hostname': hostname,
            'domain': domain,
        }

        if public_vlan:
            hardware['primaryNetworkComponent'] = {
                "networkVlan": {"id": int(public_vlan)}}
        if private_vlan:
            hardware['primaryBackendNetworkComponent'] = {
                "networkVlan": {"id": int(private_vlan)}}

        order = {
            'hardware': [hardware],
            'location': _get_location_key(package, location),
            'prices': [{'id': price} for price in prices],
            'packageId': package['id'],
            'presetId': _get_preset_id(package, size),
            'useHourlyPricing': hourly,
        }

        if post_uri:
            order['provisionScripts'] = [post_uri]

        if ssh_keys:
            order['sshKeys'] = [{'sshKeyIds': ssh_keys}]

        return order

    def _get_ids_from_hostname(self, hostname):
        """Returns list of matching hardware IDs for a given hostname."""
        results = self.list_hardware(hostname=hostname, mask="id")
        return [result['id'] for result in results]

    def _get_ids_from_ip(self, ip):
        """Returns list of matching hardware IDs for a given ip address."""
        try:
            # Does it look like an ip address?
            socket.inet_aton(ip)
        except socket.error:
            return []

        # Find the server via ip address. First try public ip, then private
        results = self.list_hardware(public_ip=ip, mask="id")
        if results:
            return [result['id'] for result in results]

        results = self.list_hardware(private_ip=ip, mask="id")
        if results:
            return [result['id'] for result in results]

    def edit(self, hardware_id, userdata=None, hostname=None, domain=None,
             notes=None):
        """Edit hostname, domain name, notes, user data of the hardware.

        Parameters set to None will be ignored and not attempted to be updated.

        :param integer hardware_id: the instance ID to edit
        :param string userdata: user data on the hardware to edit.
                                If none exist it will be created
        :param string hostname: valid hostname
        :param string domain: valid domain name
        :param string notes: notes about this particular hardware

        """

        obj = {}
        if userdata:
            self.hardware.setUserMetadata([userdata], id=hardware_id)

        if hostname:
            obj['hostname'] = hostname

        if domain:
            obj['domain'] = domain

        if notes:
            obj['notes'] = notes

        if not obj:
            return True

        return self.hardware.editObject(obj, id=hardware_id)

    def update_firmware(self,
                        hardware_id,
                        ipmi=True,
                        raid_controller=True,
                        bios=True,
                        hard_drive=True):
        """Update hardware firmware.

        This will cause the server to be unavailable for ~20 minutes.

        :param int hardware_id: The ID of the hardware to have its firmware
                                updated.
        :param bool ipmi: Update the ipmi firmware.
        :param bool raid_controller: Update the raid controller firmware.
        :param bool bios: Update the bios firmware.
        :param bool hard_drive: Update the hard drive firmware.
        """

        return self.hardware.createFirmwareUpdateTransaction(
            bool(ipmi), bool(raid_controller), bool(bios), bool(hard_drive),
            id=hardware_id)


def _get_extra_price_id(items, key_name, hourly):
    """Returns a price id attached to item with the given key_name."""

    for item in items:
        if not utils.lookup(item, 'keyName') == key_name:
            continue

        for price in item['prices']:
            if _matches_billing(price, hourly):
                return price['id']

    raise SoftLayer.SoftLayerError(
        "Could not find valid price for extra option, '%s'" % key_name)


def _get_default_price_id(items, option, hourly):
    """Returns a 'free' price id given an option."""

    for item in items:
        if not utils.lookup(item, 'itemCategory', 'categoryCode') == option:
            continue

        for price in item['prices']:
            if all([float(price.get('hourlyRecurringFee', 0)) == 0.0,
                    float(price.get('recurringFee', 0)) == 0.0,
                    _matches_billing(price, hourly)]):
                return price['id']

    raise SoftLayer.SoftLayerError(
        "Could not find valid price for '%s' option" % option)


def _get_bandwidth_price_id(items, hourly=True, no_public=False):
    """Choose a valid price id for bandwidth."""

    # Prefer pay-for-use data transfer with hourly
    for item in items:

        capacity = float(item.get('capacity', 0))
        # Hourly and private only do pay-as-you-go bandwidth
        if any([not utils.lookup(item,
                                 'itemCategory',
                                 'categoryCode') == 'bandwidth',
                (hourly or no_public) and capacity != 0.0,
                not (hourly or no_public) and capacity == 0.0]):
            continue

        for price in item['prices']:
            if _matches_billing(price, hourly):
                return price['id']

    raise SoftLayer.SoftLayerError(
        "Could not find valid price for bandwidth option")


def _get_os_price_id(items, os):
    """Returns the price id matching."""

    for item in items:
        if any([not utils.lookup(item,
                                 'itemCategory',
                                 'categoryCode') == 'os',
                not utils.lookup(item,
                                 'softwareDescription',
                                 'referenceCode') == os]):
            continue

        for price in item['prices']:
            return price['id']

    raise SoftLayer.SoftLayerError("Could not find valid price for os: '%s'" %
                                   os)


def _get_port_speed_price_id(items, port_speed, no_public):
    """Choose a valid price id for port speed."""

    for item in items:
        if not utils.lookup(item,
                            'itemCategory',
                            'categoryCode') == 'port_speed':
            continue

        # Check for correct capacity and if the item matches private only
        if any([int(utils.lookup(item, 'capacity')) != port_speed,
                _is_private_port_speed_item(item) != no_public]):
            continue

        for price in item['prices']:
            return price['id']

    raise SoftLayer.SoftLayerError(
        "Could not find valid price for port speed: '%s'" % port_speed)


def _matches_billing(price, hourly):
    """Return if the price object is hourly and/or monthly."""
    return any([hourly and price.get('hourlyRecurringFee') is not None,
                not hourly and price.get('recurringFee') is not None])


def _is_private_port_speed_item(item):
    """Determine if the port speed item is private network only."""
    for attribute in item['attributes']:
        if attribute['attributeTypeKeyName'] == 'IS_PRIVATE_NETWORK_ONLY':
            return True

    return False


def _get_location_key(package, location):
    """Get the longer key with a short location name."""
    for region in package['regions']:
        if region['location']['location']['name'] == location:
            return region['keyname']

    raise SoftLayer.SoftLayerError("Could not find valid location for: '%s'"
                                   % location)


def _get_preset_id(package, size):
    """Get the preset id given the keyName of the preset."""
    for preset in package['activePresets']:
        if preset['keyName'] == size:
            return preset['id']

    raise SoftLayer.SoftLayerError("Could not find valid size for: '%s'"
                                   % size)
