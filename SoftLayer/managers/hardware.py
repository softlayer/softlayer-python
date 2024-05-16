"""
    SoftLayer.hardware
    ~~~~~~~~~~~~~~~~~~
    Hardware Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
import concurrent.futures as cf
import datetime
import logging
import socket
import time

from SoftLayer.decoration import retry
from SoftLayer import exceptions
from SoftLayer.exceptions import SoftLayerError
from SoftLayer.managers import ordering
from SoftLayer.managers.ticket import TicketManager
from SoftLayer import utils

LOGGER = logging.getLogger(__name__)

# Invalid names are ignored due to long method names and short argument names
# pylint: disable=invalid-name, too-many-lines, too-many-public-methods

EXTRA_CATEGORIES = ['pri_ipv6_addresses',
                    'static_ipv6_addresses',
                    'sec_ip_addresses',
                    'trusted_platform_module',
                    'software_guard_extensions']


class HardwareManager(utils.IdentifierMixin, object):
    """Manage SoftLayer hardware servers.

    Example::

       # Initialize the Manager.
       # env variables. These can also be specified in ~/.softlayer,
       # or passed directly to SoftLayer.Client()
       # SL_USERNAME = YOUR_USERNAME
       # SL_API_KEY = YOUR_API_KEY
       import SoftLayer
       client = SoftLayer.Client()
       mgr = SoftLayer.HardwareManager(client)

    See product information here: https://www.ibm.com/cloud/bare-metal-servers

    :param SoftLayer.API.BaseClient client: the client instance
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
        self.package_keyname = 'BARE_METAL_SERVER'
        if ordering_manager is None:
            self.ordering_manager = ordering.OrderingManager(client)
        else:
            self.ordering_manager = ordering_manager

    def cancel_hardware(self, hardware_id, reason='unneeded', comment='', immediate=False):
        """Cancels the specified dedicated server.

        Example::

            # Cancels hardware id 1234
            result = mgr.cancel_hardware(hardware_id=1234)

        :param int hardware_id: The ID of the hardware to be cancelled.
        :param string reason: The reason code for the cancellation. This should come from
                              :func:`get_cancellation_reasons`.
        :param string comment: An optional comment to include with the cancellation.
        :param bool immediate: If set to True, will automatically update the cancelation ticket to request
                               the resource be reclaimed asap. This request still has to be reviewed by a human
        :returns: True on success or an exception
        """

        # Get cancel reason
        reasons = self.get_cancellation_reasons()
        cancel_reason = reasons.get(reason, reasons['unneeded'])
        ticket_mgr = TicketManager(self.client)
        mask = 'mask[id, hourlyBillingFlag, billingItem[id], openCancellationTicket[id], activeTransaction]'
        hw_billing = self.get_hardware(hardware_id, mask=mask)

        if 'activeTransaction' in hw_billing:
            raise SoftLayerError("Unable to cancel hardware with running transaction")

        if 'billingItem' not in hw_billing:
            if utils.lookup(hw_billing, 'openCancellationTicket', 'id'):
                raise SoftLayerError("Ticket #%s already exists for this server" %
                                     hw_billing['openCancellationTicket']['id'])
            raise SoftLayerError("Cannot locate billing for the server. The server may already be cancelled.")

        billing_id = hw_billing['billingItem']['id']

        if immediate and not hw_billing['hourlyBillingFlag']:
            LOGGER.warning("Immediate cancellation of monthly servers is not guaranteed."
                           "Please check the cancellation ticket for updates.")

            result = self.client.call('Billing_Item', 'cancelItem',
                                      False, False, cancel_reason, comment, id=billing_id)
            hw_billing = self.get_hardware(hardware_id, mask=mask)
            ticket_number = hw_billing['openCancellationTicket']['id']
            cancel_message = "Please reclaim this server ASAP, it is no longer needed. Thankyou."
            ticket_mgr.update_ticket(ticket_number, cancel_message)
            LOGGER.info("Cancelation ticket #%s has been updated requesting immediate reclaim", ticket_number)
        else:
            result = self.client.call('Billing_Item', 'cancelItem',
                                      immediate, False, cancel_reason, comment, id=billing_id)
            hw_billing = self.get_hardware(hardware_id, mask=mask)
            ticket_number = hw_billing['openCancellationTicket']['id']
            LOGGER.info("Cancelation ticket #%s has been created", ticket_number)

        return result

    @retry(logger=LOGGER)
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

       Example::

            # Using a custom object-mask. Will get ONLY what is specified
            # These will stem from the SoftLayer_Hardware_Server datatype
            object_mask = "mask[hostname,monitoringRobot[robotStatus]]"
            result = mgr.list_hardware(mask=object_mask)
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
        kwargs['iter'] = True
        return self.client.call('Account', 'getHardware', **kwargs)

    @retry(logger=LOGGER)
    def get_hardware(self, hardware_id, **kwargs):
        """Get details about a hardware device.

        :param integer id: the hardware ID
        :returns: A dictionary containing a large amount of information about
                  the specified server.

        Example::

            object_mask = "mask[id,networkVlans[vlanNumber]]"
            # Object masks are optional
            result = mgr.get_hardware(hardware_id=1234,mask=object_mask)
        """

        if 'mask' not in kwargs:
            kwargs['mask'] = (
                'id,'
                'globalIdentifier,'
                'fullyQualifiedDomainName,'
                'hostname,'
                'domain,'
                'provisionDate,'
                'hardwareStatus,'
                'bareMetalInstanceFlag,'
                'processorPhysicalCoreAmount,'
                'memoryCapacity,'
                'notes,'
                'privateNetworkOnlyFlag,'
                'primaryBackendIpAddress,'
                'primaryIpAddress,'
                'networkManagementIpAddress,'
                'userData,'
                'activeComponents[id,hardwareComponentModel['
                'hardwareGenericComponentModel[id,hardwareComponentType[keyName]]]],'
                'datacenter,'
                '''networkComponents[id, status, speed, maxSpeed, name,
                   ipmiMacAddress, ipmiIpAddress, macAddress, primaryIpAddress,
                   port, primarySubnet[id, netmask, broadcastAddress,
                                       networkIdentifier, gateway]],'''
                'hardwareChassis[id,name],'
                'activeTransaction[id, transactionStatus[friendlyName,name]],'
                '''operatingSystem[
                    softwareLicense[softwareDescription[manufacturer,
                                                        name,
                                                        version,
                                                        referenceCode]],
                    passwords[username,password]],'''
                '''softwareComponents[
                    softwareLicense[softwareDescription[manufacturer,
                                                        name,
                                                        version,
                                                        referenceCode]],
                    passwords[id,username,password]],'''
                'billingItem['
                'id,nextInvoiceTotalRecurringAmount,'
                'nextInvoiceChildren[nextInvoiceTotalRecurringAmount],'
                'orderItem.order.userRecord[username]'
                '],'
                'lastTransaction[transactionGroup],'
                'hourlyBillingFlag,'
                'tagReferences[id,tag[name,id]],'
                'networkVlans[id,vlanNumber,networkSpace, fullyQualifiedName,primarySubnets[ipAddresses]],'
                'monitoringServiceComponent,networkMonitors[queryType,lastResult,responseAction],'
                'remoteManagementAccounts[username,password]'
            )

        return self.hardware.getObject(id=hardware_id, **kwargs)

    @retry(logger=LOGGER)
    def get_hardware_fast(self, hardware_id):
        """Get details about a hardware device. Similar to get_hardware() but this uses threads

        :param integer id: the hardware ID
        :returns: A dictionary containing a large amount of information about the specified server.
        """

        hw_mask = (
            'id, globalIdentifier, fullyQualifiedDomainName, hostname, domain,'
            'provisionDate, hardwareStatus, bareMetalInstanceFlag, processorPhysicalCoreAmount,'
            'memoryCapacity, notes, privateNetworkOnlyFlag, primaryBackendIpAddress,'
            'primaryIpAddress, networkManagementIpAddress, userData, datacenter, hourlyBillingFlag,'
            'lastTransaction[transactionGroup], hardwareChassis[id,name]'
        )
        server = self.client.call('SoftLayer_Hardware_Server', 'getObject', id=hardware_id, mask=hw_mask)
        with cf.ThreadPoolExecutor(max_workers=10) as executor:
            networkComponentsMask = (
                "id, status, speed, maxSpeed, name, ipmiMacAddress, ipmiIpAddress, macAddress, primaryIpAddress,"
                "port, primarySubnet[id, netmask, broadcastAddress, networkIdentifier, gateway],"
                "uplinkComponent[networkVlanTrunks[networkVlan[networkSpace]]]"
            )
            networkComponents = executor.submit(
                self.client.call, 'SoftLayer_Hardware_Server', 'getNetworkComponents',
                id=hardware_id, mask=networkComponentsMask
            )
            activeComponentsMask = (
               'id,hardwareComponentModel[hardwareGenericComponentModel[id,hardwareComponentType[keyName]]]'
            )
            activeComponents = executor.submit(
                self.client.call, 'SoftLayer_Hardware_Server', 'getActiveComponents',
                id=hardware_id, mask=activeComponentsMask
            )

            activeTransaction = executor.submit(
                self.client.call, 'SoftLayer_Hardware_Server', 'getActiveTransaction',
                id=hardware_id, mask="id, transactionStatus[friendlyName,name]"
            )

            operatingSystemMask = (
                'softwareLicense[softwareDescription[manufacturer, name, version, referenceCode]],'
                'passwords[id,username,password]'
            )
            operatingSystem = executor.submit(
                self.client.call, 'SoftLayer_Hardware_Server', 'getOperatingSystem',
                id=hardware_id, mask=operatingSystemMask
            )

            # Intentionally reusing the operatingSystemMask here. They are both softwareComponents
            softwareComponents = executor.submit(
                self.client.call, 'SoftLayer_Hardware_Server', 'getSoftwareComponents',
                id=hardware_id, mask=operatingSystemMask
            )

            billingItemMask = (
                'id,nextInvoiceTotalRecurringAmount,'
                'nextInvoiceChildren[nextInvoiceTotalRecurringAmount],'
                'orderItem.order.userRecord[username]'
            )
            billingItem = executor.submit(
                self.client.call, 'SoftLayer_Hardware_Server', 'getBillingItem',
                id=hardware_id, mask=billingItemMask
            )

            tagReferences = executor.submit(
                self.client.call, 'SoftLayer_Hardware_Server', 'getTagReferences',
                id=hardware_id, mask="id,tag[name,id]"
            )

            networkVlans = executor.submit(
                self.client.call, 'SoftLayer_Hardware_Server', 'getNetworkVlans',
                id=hardware_id, mask="id,vlanNumber,networkSpace,fullyQualifiedName,primarySubnets[ipAddresses]"
            )

            remoteManagementAccounts = executor.submit(
                self.client.call, 'SoftLayer_Hardware_Server', 'getRemoteManagementAccounts',
                id=hardware_id, mask="username,password"
            )

            server['networkComponents'] = networkComponents.result()
            server['activeComponents'] = activeComponents.result()
            server['activeTransaction'] = activeTransaction.result()
            server['operatingSystem'] = operatingSystem.result()
            server['softwareComponents'] = softwareComponents.result()
            server['billingItem'] = billingItem.result()
            server['networkVlans'] = networkVlans.result()
            server['remoteManagementAccounts'] = remoteManagementAccounts.result()
            server['tagReferences'] = tagReferences.result()

        return server

    def reload(self, hardware_id, post_uri=None, ssh_keys=None, lvm=False):
        """Perform an OS reload of a server with its current configuration.

        https://sldn.softlayer.com/reference/datatypes/SoftLayer_Container_Hardware_Server_Configuration/
        :param integer hardware_id: the instance ID to reload
        :param string post_uri: The URI of the post-install script to run after reload
        :param list ssh_keys: The SSH keys to add to the root user
        :param bool lvm: A flag indicating that the provision should use LVM for all logical drives.
        """

        config = {}

        if post_uri:
            config['customProvisionScriptUri'] = post_uri

        if ssh_keys:
            config['sshKeyIds'] = list(ssh_keys)
        if lvm:
            config['lvmFlag'] = lvm

        return self.hardware.reloadOperatingSystem('FORCE', config, id=hardware_id)

    def rescue(self, hardware_id):
        """Reboot a server into the a recsue kernel.

        :param integer instance_id: the server ID to rescue

        Example::

            result = mgr.rescue(1234)
        """
        return self.hardware.bootToRescueLayer(id=hardware_id)

    def change_port_speed(self, hardware_id, public, speed, redundant=None):
        """Allows you to change the port speed of a server's NICs.

        :param int hardware_id: The ID of the server
        :param bool public: Flag to indicate which interface to change.
                            True (default) means the public interface.
                            False indicates the private interface.
        :param int speed: The port speed to set.

        .. warning::
            A port speed of 0 will disable the interface.

        Example::

            #change the Public interface to 10Mbps on instance 12345
            result = mgr.change_port_speed(hardware_id=12345,
                                           public=True, speed=10)
            # result will be True or an Exception
        """
        if public:
            return self.client.call('Hardware_Server',
                                    'setPublicNetworkInterfaceSpeed',
                                    [speed, redundant], id=hardware_id)
        else:
            return self.client.call('Hardware_Server',
                                    'setPrivateNetworkInterfaceSpeed',
                                    [speed, redundant], id=hardware_id)

    def place_order(self, **kwargs):
        """Places an order for a piece of hardware.

        See get_create_options() for valid arguments.

        :param string size: server size name or presetId
        :param string hostname: server hostname
        :param string domain: server domain name
        :param string location: location (datacenter) name
        :param string os: operating system name
        :param int port_speed: Port speed in Mbps
        :param list ssh_keys: list of ssh key ids
        :param string post_uri: The URI of the post-install script to run after reload
        :param boolean hourly: True if using hourly pricing (default). False for monthly.
        :param boolean no_public: True if this server should only have private interfaces
        :param list extras: List of extra feature names
        """
        create_options = self._generate_create_dict(**kwargs)
        return self.ordering_manager.place_order(**create_options)
        # return self.client['Product_Order'].placeOrder(create_options)

    def verify_order(self, **kwargs):
        """Verifies an order for a piece of hardware.

        See :func:`place_order` for a list of available options.
        """
        create_options = self._generate_create_dict(**kwargs)
        return self.ordering_manager.verify_order(**create_options)

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

    @retry(logger=LOGGER)
    def get_create_options(self, datacenter=None):
        """Returns valid options for ordering hardware.

        :param string datacenter: short name, like dal09
        """

        package = self._get_package()

        location_group_id = None
        if datacenter:
            _filter = {"name": {"operation": datacenter}}
            _mask = "mask[priceGroups]"
            dc_details = self.client.call('SoftLayer_Location', 'getDatacenters', mask=_mask, filter=_filter, limit=1)
            if not dc_details:
                raise SoftLayerError(f"Unable to find a datacenter named {datacenter}")
            # A DC will have several price groups, no good way to deal with this other than checking each.
            # An item should only belong to one type of price group.
            for group in dc_details[0].get('priceGroups', []):
                # We only care about SOME of the priceGroups, which all SHOULD start with `Location Group X`
                # Hopefully this never changes....
                if group.get('description').startswith('Location'):
                    location_group_id = group.get('id')

        # Locations
        locations = []
        for region in package['regions']:
            if datacenter is None or datacenter == region['location']['location']['name']:
                locations.append({
                    'name': region['location']['location']['longName'],
                    'key': region['location']['location']['name'],
                })
        # Sizes
        sizes = []
        for preset in package['activePresets'] + package['accountRestrictedActivePresets']:
            sizes.append({
                'name': preset['description'],
                'key': preset['keyName'],
                'hourlyRecurringFee': _get_preset_cost(preset, package['items'], 'hourly', location_group_id),
                'recurringFee': _get_preset_cost(preset, package['items'], 'monthly', location_group_id)
            })

        operating_systems = []
        port_speeds = []
        extras = []
        for item in package['items']:
            category = item['itemCategory']['categoryCode']
            # Operating systems
            if category == 'os':
                operating_systems.append({
                    'name': item['softwareDescription']['longDescription'],
                    'key': item['keyName'],
                    'referenceCode': item['softwareDescription']['referenceCode'],
                    'prices': get_item_price(item['prices'], location_group_id)
                })
            # Port speeds
            elif category == 'port_speed':
                port_speeds.append({
                    'name': item['description'],
                    'speed': item['capacity'],
                    'key': item['keyName'],
                    'prices': get_item_price(item['prices'], location_group_id)
                })
            # Extras
            elif category in EXTRA_CATEGORIES:
                extras.append({
                    'name': item['description'],
                    'key': item['keyName'],
                    'prices': get_item_price(item['prices'], location_group_id)
                })

        return {
            'locations': locations,
            'sizes': sizes,
            'operating_systems': operating_systems,
            'port_speeds': port_speeds,
            'extras': extras,
        }

    @retry(logger=LOGGER)
    def _get_package(self):
        """Get the package related to simple hardware ordering."""
        items_mask = 'mask[id,keyName,capacity,description,attributes[id,attributeTypeKeyName],' \
                     'itemCategory[id,categoryCode],softwareDescription[id,referenceCode,longDescription],' \
                     'prices[categories]]'
        # The preset prices list will only have default prices. The prices->item->prices will have location specific
        presets_mask = 'mask[prices]'
        region_mask = 'location[location[priceGroups]]'
        package = {'items': [], 'activePresets': [], 'accountRestrictedActivePresets': [], 'regions': []}
        package_info = self.ordering_manager.get_package_by_key(self.package_keyname, mask="mask[id]")

        package['items'] = self.client.call('SoftLayer_Product_Package', 'getItems',
                                            id=package_info.get('id'), mask=items_mask)
        package['activePresets'] = self.client.call('SoftLayer_Product_Package', 'getActivePresets',
                                                    id=package_info.get('id'), mask=presets_mask)
        package['accountRestrictedActivePresets'] = self.client.call('SoftLayer_Product_Package',
                                                                     'getAccountRestrictedActivePresets',
                                                                     id=package_info.get('id'), mask=presets_mask)
        package['regions'] = self.client.call('SoftLayer_Product_Package', 'getRegions',
                                              id=package_info.get('id'), mask=region_mask)
        return package

    def _generate_create_dict(self,
                              size=None,
                              hostname=None,
                              domain=None,
                              location=None,
                              os=None,
                              port_speed=None,
                              ssh_keys=None,
                              post_uri=None,
                              hourly=True,
                              no_public=False,
                              extras=None,
                              network=None,
                              public_router=None,
                              private_router=None):
        """Translates arguments into a dictionary for creating a server."""

        extras = extras or []

        package = self._get_package()
        items = package.get('items', {})
        location_id = _get_location(package, location)

        key_names = [
            '1_IP_ADDRESS',
            'UNLIMITED_SSL_VPN_USERS_1_PPTP_VPN_USER_PER_ACCOUNT',
            'REBOOT_KVM_OVER_IP'
        ]

        # Operating System
        key_names.append(os)

        # Bandwidth Options
        key_names.append(
            _get_bandwidth_key(items, hourly=hourly, no_public=no_public, location=location_id)
        )

        # Port Speed Options
        # New option in v5.9.0
        if network:
            key_names.append(network)
        # Legacy Option, doesn't support bonded/redundant
        else:
            key_names.append(
                _get_port_speed_key(items, port_speed, no_public, location=location_id)
            )

        # Extras
        for extra in extras:
            key_names.append(extra)

        extras = {
            'hardware': [{
                'hostname': hostname,
                'domain': domain,
            }]
        }
        if private_router:
            extras['hardware'][0]['primaryBackendNetworkComponent'] = {"router": {"id": int(private_router)}}
        if public_router:
            extras['hardware'][0]['primaryNetworkComponent'] = {"router": {"id": int(public_router)}}
        if post_uri:
            extras['provisionScripts'] = [post_uri]

        if ssh_keys:
            extras['sshKeys'] = [{'sshKeyIds': ssh_keys}]

        order = {
            'package_keyname': self.package_keyname,
            'location': location,
            'item_keynames': key_names,
            'complex_type': 'SoftLayer_Container_Product_Order_Hardware_Server',
            'hourly': hourly,
            'preset_keyname': size,
            'extras': extras,
            'quantity': 1,
        }
        return order

    def _get_ids_from_hostname(self, hostname):
        """Returns list of matching hardware IDs for a given hostname."""
        results = self.list_hardware(hostname=hostname, mask="id")
        return [result['id'] for result in results]

    def _get_ids_from_ip(self, ip):  # pylint: disable=inconsistent-return-statements
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
             notes=None, tags=None):
        """Edit hostname, domain name, notes, user data of the hardware.

        Parameters set to None will be ignored and not attempted to be updated.

        :param integer hardware_id: the instance ID to edit
        :param string userdata: user data on the hardware to edit.
                                If none exist it will be created
        :param string hostname: valid hostname
        :param string domain: valid domain name
        :param string notes: notes about this particular hardware
        :param string tags: tags to set on the hardware as a comma separated
                            list. Use the empty string to remove all tags.

        Example::

            # Change the hostname on instance 12345 to 'something'
            result = mgr.edit(hardware_id=12345 , hostname="something")
            #result will be True or an Exception
        """

        obj = {}
        if userdata:
            self.hardware.setUserMetadata([userdata], id=hardware_id)

        if tags is not None:
            self.hardware.setTags(tags, id=hardware_id)

        if hostname:
            obj['hostname'] = hostname

        if domain:
            obj['domain'] = domain

        if notes:
            obj['notes'] = notes

        if not obj:
            return True

        return self.hardware.editObject(obj, id=hardware_id)

    def update_firmware(self, hardware_id: int,
                        ipmi: bool = True,
                        raid_controller: bool = True,
                        bios: bool = True,
                        hard_drive: bool = True,
                        network: bool = True):
        """Update hardware firmware.

        This will cause the server to be unavailable for ~20 minutes.
        https://sldn.softlayer.com/reference/services/SoftLayer_Hardware_Server/createFirmwareUpdateTransaction/

        :param int hardware_id: The ID of the hardware to have its firmware updated.
        :param bool ipmi: Update the ipmi firmware.
        :param bool raid_controller: Update the raid controller firmware.
        :param bool bios: Update the bios firmware.
        :param bool hard_drive: Update the hard drive firmware.
        :param bool network: Update the network card firmware

        Example::

            # Check the servers active transactions to see progress
            result = mgr.update_firmware(hardware_id=1234)
        """

        return self.client.call(
            'SoftLayer_Hardware_Server', 'createFirmwareUpdateTransaction',
            bool(ipmi), bool(raid_controller), bool(bios), bool(hard_drive), bool(network), id=hardware_id
        )

    def reflash_firmware(self, hardware_id: int,
                         ipmi: bool = True,
                         raid_controller: bool = True,
                         bios: bool = True,):
        """Reflash hardware firmware.

        This will cause the server to be unavailable for ~60 minutes.
        The firmware will not be upgraded but rather reflashed to the version installed.
        https://sldn.softlayer.com/reference/services/SoftLayer_Hardware_Server/createFirmwareReflashTransaction/

        :param int hardware_id: The ID of the hardware to have its firmware reflashed.
        :param bool ipmi: Reflash the ipmi firmware.
        :param bool raid_controller: Reflash the raid controller firmware.
        :param bool bios: Reflash the bios firmware.

        Example::

            # Check the servers active transactions to see progress
            result = mgr.reflash_firmware(hardware_id=1234)
        """

        return self.hardware.createFirmwareReflashTransaction(
            bool(ipmi), bool(raid_controller), bool(bios), id=hardware_id)

    def wait_for_ready(self, instance_id, limit=14400, delay=10, pending=False):
        """Determine if a Server is ready.

        A server is ready when no transactions are running on it.

        :param int instance_id: The instance ID with the pending transaction
        :param int limit: The maximum amount of seconds to wait.
        :param int delay: The number of seconds to sleep before checks. Defaults to 10.
        """
        now = time.time()
        until = now + limit
        mask = "mask[id, lastOperatingSystemReload[id], activeTransaction, provisionDate]"
        instance = self.get_hardware(instance_id, mask=mask)
        while now <= until:
            if utils.is_ready(instance, pending):
                return True
            transaction = utils.lookup(instance, 'activeTransaction', 'transactionStatus', 'friendlyName')
            snooze = min(delay, until - now)
            LOGGER.info("%s - %d not ready. Auto retry in %ds", transaction, instance_id, snooze)
            time.sleep(snooze)
            instance = self.get_hardware(instance_id, mask=mask)
            now = time.time()

        LOGGER.info("Waiting for %d expired.", instance_id)
        return False

    def get_tracking_id(self, instance_id):
        """Returns the Metric Tracking Object Id for a hardware server

        :param int instance_id: Id of the hardware server
        """
        return self.hardware.getMetricTrackingObjectId(id=instance_id)

    def get_bandwidth_data(self, instance_id, start_date=None, end_date=None, direction=None, rollup=3600):
        """Gets bandwidth data for a server

        Will get averaged bandwidth data for a given time period. If you use a rollup over 3600 be aware
        that the API will bump your start/end date to align with how data is stored. For example if you
        have a rollup of 86400 your start_date will be bumped to 00:00. If you are not using a time in the
        start/end date fields, this won't really matter.

        :param int instance_id: Hardware Id to get data for
        :param date start_date: Date to start pulling data for.
        :param date end_date: Date to finish pulling data for
        :param string direction: Can be either 'public', 'private', or None for both.
        :param int rollup: 300, 600, 1800, 3600, 43200 or 86400 seconds to average data over.
        """
        tracking_id = self.get_tracking_id(instance_id)
        data = self.client.call('Metric_Tracking_Object', 'getBandwidthData', start_date, end_date, direction,
                                rollup, id=tracking_id, iter=True)
        return data

    def get_bandwidth_allocation(self, instance_id):
        """Combines getBandwidthAllotmentDetail() and getBillingCycleBandwidthUsage() """
        a_mask = "mask[allocation[amount]]"
        allotment = self.client.call('Hardware_Server', 'getBandwidthAllotmentDetail', id=instance_id, mask=a_mask)
        u_mask = "mask[amountIn,amountOut,type]"
        usage = self.client.call('Hardware_Server', 'getBillingCycleBandwidthUsage', id=instance_id, mask=u_mask)
        if allotment:
            return {'allotment': allotment.get('allocation'), 'usage': usage}
        return {'allotment': allotment, 'usage': usage}

    def get_storage_details(self, instance_id, nas_type):
        """Returns the hardware server attached network storage.

        :param int instance_id: Id of the hardware server
        :param nas_type: storage type.
        """
        mask = 'mask[id,username,capacityGb,notes,serviceResourceBackendIpAddress,' \
               'allowedHardware[id,datacenter]]'
        return self.hardware.getAttachedNetworkStorages(nas_type, mask=mask, id=instance_id)

    def get_storage_credentials(self, instance_id):
        """Returns the hardware server storage credentials.

        :param int instance_id: Id of the hardware server
        """
        mask = 'mask[credential]'
        return self.hardware.getAllowedHost(mask=mask, id=instance_id)

    def get_hard_drives(self, instance_id):
        """Returns the hardware server hard drives.

        :param int instance_id: Id of the hardware server
        """
        return self.hardware.getHardDrives(id=instance_id)

    def get_hardware_item_prices(self, location):
        """Returns the hardware server item prices by location.

        :param string location: location to get the item prices.
        """
        object_mask = "filteredMask[pricingLocationGroup[locations[regions]]]"
        object_filter = {
            "itemPrices": {"pricingLocationGroup": {"locations": {"regions": {"keyname": {"operation": location}}}}}}
        package = self.ordering_manager.get_package_by_key(self.package_keyname)
        return self.client.call('SoftLayer_Product_Package', 'getItemPrices', mask=object_mask, filter=object_filter,
                                id=package['id'])

    def authorize_storage(self, hardware_id, username_storage):
        """Authorize File or Block Storage to a Hardware Server.

        :param int hardware_id: Hardware server id.
        :param string username_storage: Storage username.

        :return: bool.
        """
        _filter = {"networkStorage": {"username": {"operation": username_storage}}}

        storage_result = self.client.call('Account', 'getNetworkStorage', filter=_filter)

        if len(storage_result) == 0:
            raise SoftLayerError("The Storage with username: %s was not found, please"
                                 " enter a valid storage username" % username_storage)

        storage_template = [
            {
                "id": storage_result[0]['id'],
                "username": username_storage
            }
        ]

        result = self.client.call('Hardware', 'allowAccessToNetworkStorageList',
                                  storage_template, id=hardware_id)

        return result

    def upgrade(self, instance_id, memory=None,
                nic_speed=None, drive_controller=None,
                public_bandwidth=None, disk=None, test=False):
        """Upgrades a hardware server instance.

        :param int instance_id: Instance id of the hardware server to be upgraded.
        :param int memory: Memory size.
        :param string nic_speed: Network Port Speed data.
        :param string drive_controller: Drive Controller data.
        :param int public_bandwidth: Public keyName data.
        :param list disk: List of disks to add or upgrade Hardware Server.
        :param bool test: Test option to verify the request.

        :returns: bool
        """
        result = None
        maintenance_window_id = None
        upgrade_prices = self._get_upgrade_prices(instance_id)
        prices = []
        data = {}

        if memory:
            data['memory'] = memory
        if nic_speed:
            data['nic_speed'] = nic_speed
        if drive_controller:
            data['disk_controller'] = drive_controller
        if public_bandwidth:
            data['bandwidth'] = public_bandwidth

        server_response = self.get_instance(instance_id)
        package_id = server_response['billingItem']['package']['id']
        location_id = server_response['datacenter']['id']

        maintenance_window = datetime.datetime.now(utils.UTC())
        maintenance_window_detail = self.get_maintenance_windows_detail(location_id)
        if maintenance_window_detail:
            maintenance_window_id = maintenance_window_detail.get('id')

        order = {
            'complexType': 'SoftLayer_Container_Product_Order_Hardware_Server_Upgrade',
            'properties': [
                {
                    'name': 'MAINTENANCE_WINDOW',
                    'value': maintenance_window.strftime("%Y-%m-%d %H:%M:%S%z")
                },
                {
                    'name': 'MAINTENANCE_WINDOW_ID',
                    'value': str(maintenance_window_id)
                }

            ],
            'hardware': [{'id': int(instance_id)}],
            'packageId': package_id
        }

        if disk:
            prices = self._get_disk_price_list(instance_id, disk)
            order['prices'] = prices

        for option, value in data.items():
            price_id = self._get_prices_for_upgrade_option(upgrade_prices, option, value)
            if not price_id:
                # Every option provided is expected to have a price
                raise exceptions.SoftLayerError(
                    "Unable to find %s option with value %s" % (option, value))

            prices.append({'id': price_id})

            order['prices'] = prices

        if prices:
            if test:
                result = self.client['Product_Order'].verifyOrder(order)
            else:
                result = self.client['Product_Order'].placeOrder(order)
        return result

    def get_maintenance_windows_detail(self, location_id):
        """Get the disks prices to be added or upgraded.

        :param int location_id: Hardware Server location id.
        :return int:
        """
        result = None
        begin_date_object = datetime.datetime.now()
        begin_date = begin_date_object.strftime("%Y-%m-%dT00:00:00.0000-06:00")
        end_date_object = datetime.date.today() + datetime.timedelta(days=30)
        end_date = end_date_object.strftime("%Y-%m-%dT00:00:00.0000-06:00")

        result_windows = self.client['SoftLayer_Provisioning_Maintenance_Window'].getMaintenanceWindows(begin_date,
                                                                                                        end_date,
                                                                                                        location_id)
        if len(result_windows) > 0:
            result = result_windows[0]

        return result

    @retry(logger=LOGGER)
    def get_instance(self, instance_id):
        """Get details about a hardware server instance.

        :param int instance_id: the instance ID
        :returns: A dictionary containing a large amount of information about
                  the specified instance.
        """
        mask = [
            'datacenter,billingItem[id,package[id,keyName],nextInvoiceChildren]'
        ]
        mask = "mask[%s]" % ','.join(mask)

        return self.hardware.getObject(id=instance_id, mask=mask)

    def _get_upgrade_prices(self, instance_id):
        """Following Method gets all the price ids related to upgrading a Hardware Server.

        :param int instance_id: Instance id of the Hardware Server to be upgraded.

        :returns: list
        """
        mask = [
            'id',
            'locationGroupId',
            'categories[name,id,categoryCode]',
            'item[keyName,description,capacity,units]'
        ]
        mask = "mask[%s]" % ','.join(mask)
        return self.hardware.getUpgradeItemPrices(id=instance_id, mask=mask)

    @staticmethod
    def _get_prices_for_upgrade_option(upgrade_prices, option, value):
        """Find the price id for the option and value to upgrade. This

        :param list upgrade_prices: Contains all the prices related to a
        hardware server upgrade.
        :param string option: Describes type of parameter to be upgraded

        :return: int.
        """
        price_id = None
        option_category = {
            'memory': 'ram',
            'nic_speed': 'port_speed',
            'disk_controller': 'disk_controller',
            'bandwidth': 'bandwidth'
        }
        if 'disk' in option:
            category_code = option
        else:
            category_code = option_category.get(option)

        for price in upgrade_prices:
            if price.get('categories') is None or price.get('item') is None:
                continue

            product = price.get('item')
            for category in price.get('categories'):
                if not category.get('categoryCode') == category_code:
                    continue

                if option == 'disk_controller':
                    if value == product.get('description'):
                        price_id = price.get('id')
                elif option == 'nic_speed':
                    if value.isdigit():
                        if str(product.get('capacity')) == str(value):
                            price_id = price.get('id')
                    else:
                        split_nic_speed = value.split(" ")
                        if str(product.get('capacity')) == str(split_nic_speed[0]) and \
                                split_nic_speed[1] in product.get("description"):
                            price_id = price.get('id')
                elif option == 'bandwidth':
                    if str(product.get('capacity')) == str(value):
                        price_id = price.get('id')
                elif 'disk' in option:
                    if str(product.get('capacity')) == str(value):
                        price_id = price
                else:
                    if str(product.get('capacity')) == str(value):
                        price_id = price.get('id')

        return price_id

    def _get_disk_price_list(self, instance_id, disk):
        """Get the disks prices to be added or upgraded.

        :param int instance_id: Hardware Server instance id.
        :param list disk: List of disks to be added o upgraded to the HW.

        :return list.
        """
        prices = []
        disk_exist = False
        upgrade_prices = self._get_upgrade_prices(instance_id)
        server_response = self.get_instance(instance_id)
        for disk_data in disk:
            disk_channel = 'disk' + str(disk_data.get('number'))
            for item in utils.lookup(server_response, 'billingItem', 'nextInvoiceChildren'):
                if disk_channel == item['categoryCode']:
                    disk_exist = True
                    break
            if disk_exist:
                disk_price_detail = self._get_disk_price_detail(disk_data, upgrade_prices, disk_channel, 'add_disk')
                prices.append(disk_price_detail)
            else:
                disk_price_detail = self._get_disk_price_detail(disk_data, upgrade_prices, disk_channel, 'resize_disk')
                prices.append(disk_price_detail)

        return prices

    def _get_disk_price_detail(self, disk_data, upgrade_prices, disk_channel, disk_type):
        """Get the disk price detail.

        :param disk_data: List of disks to be added or upgraded.
        :param list upgrade_prices: List of item prices.
        :param String disk_channel: Disk position.
        :param String disk_type: Disk type.

        """
        disk_price = {}
        if disk_data.get('description') == disk_type:
            if "add" in disk_type:
                raise SoftLayerError("Unable to add the disk because this already exists.")
            if "resize" in disk_type:
                raise SoftLayerError("Unable to resize the disk because this does not exists.")
        else:
            price_id = self._get_prices_for_upgrade_option(upgrade_prices, disk_channel,
                                                           disk_data.get('capacity'))
            if not price_id:
                raise SoftLayerError("The item price was not found for %s with 'capacity:' %i" %
                                     (disk_channel, disk_data.get('capacity')))

            disk_price = {
                "id": price_id.get('id'),
                "categories": [
                    {
                        "categoryCode": price_id['categories'][0]['categoryCode'],
                        "id": price_id['categories'][0]['id']
                    }
                ]
            }

        return disk_price

    def get_components(self, hardware_id, mask=None, filter_component=None):
        """Get details about a hardware components.

        :param int hardware_id: the instance ID
        :returns: A dictionary containing a large amount of information about
                  the specified components.
        """
        if not mask:
            mask = 'id,hardwareComponentModel[longDescription,' \
                   'hardwareGenericComponentModel[description,hardwareComponentType[keyName]],' \
                   'firmwares[createDate,version]]'

        if not filter_component:
            filter_component = {"components": {
                "hardwareComponentModel": {
                    "firmwares": {
                        "createDate": {
                            "operation": "orderBy",
                            "options": [
                                {"name": "sort", "value": ["DESC"]},
                                {"name": "sortOrder", "value": [1]}
                            ]
                        }
                    }
                }}}

        return self.client.call('Hardware_Server', 'getComponents',
                                mask=mask, filter=filter_component, id=hardware_id)

    def get_network_components(self, hardware_id, mask=None, space=None):
        """Calls SoftLayer_Hardware_Server::getNetworkComponents()

        :param int hardware_id: SoftLayer_Hardware_Server id
        :param string mask: The object mask to use if you do not want the default
        :param string space: 'public', 'private', or None for both.
        :returns: https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_Component/
        """

        if mask is None:
            mask = "mask[uplinkComponent, router, redundancyEnabledFlag, redundancyCapableFlag]"
        method = "getNetworkComponents"
        if space == "public":
            method = "getFrontendNetworkComponents"
        elif space == "private":
            method = "getBackendNetworkComponents"
        return self.client.call("SoftLayer_Hardware_Server", method, id=hardware_id, mask=mask)

    def trunk_vlan(self, component_id, vlans):
        """Calls SoftLayer_Network_Component::addNetworkVlanTrunks()

        :param int component_id: SoftLayer_Network_Component id
        :param list vlans: list of SoftLayer_Network_Vlan objects to add. Each object needs at least id or vlanNumber
        """
        return self.client.call('SoftLayer_Network_Component', 'addNetworkVlanTrunks', vlans, id=component_id)

    def remove_vlan(self, component_id, vlans):
        """Calls SoftLayer_Network_Component::removeNetworkVlanTrunks()

        :param int component_id: SoftLayer_Network_Component id
        :param list vlans: list of SoftLayer_Network_Vlan objects to remove. Each object needs at least id or vlanNumber
        """
        return self.client.call('SoftLayer_Network_Component', 'removeNetworkVlanTrunks', vlans, id=component_id)

    def clear_vlan(self, hardware_id):
        """Clears all vlan trunks from a hardware_id

        :param int hardware_id: server to clear vlans from
        """
        component_mask = (
            "mask[id, "
            "backendNetworkComponents[id,networkVlanTrunks[networkVlanId]], "
            "frontendNetworkComponents[id,networkVlanTrunks[networkVlanId]]"
            "]"
        )
        components = self.client.call('SoftLayer_Hardware_Server', 'getObject', id=hardware_id, mask=component_mask)
        # We only want to call this API on components with actual trunks.
        # Calling this on the primary and redundant components might cause exceptions.
        for c in components.get('backendNetworkComponent', []):
            if len(c.get('networkVlanTrunks', [])):
                self.client.call('SoftLayer_Network_Component', 'clearNetworkVlanTrunks', id=c.get('id'))
        for c in components.get('frontendNetworkComponent', []):
            if len(c.get('networkVlanTrunks', [])):
                self.client.call('SoftLayer_Network_Component', 'clearNetworkVlanTrunks', id=c.get('id'))

    def get_sensors(self, hardware_id):
        """Returns Hardware sensor data"""
        return self.client.call('Hardware', 'getSensorData', id=hardware_id)

    def get_notifications(self, hardware_id):
        """Returns all hardware notifications."""
        return self.client.call('SoftLayer_User_Customer_Notification_Hardware', 'findByHardwareId', hardware_id)

    def add_notification(self, hardware_id, user_id):
        """Create a user hardware notification entry"""

        template = {"hardwareId": hardware_id, "userId": user_id}
        return self.client.call('SoftLayer_User_Customer_Notification_Hardware', 'createObject', template)

    def get_software_components(self, hardware_id):
        """Returns  a piece of hardware’s installed software."""
        return self.client.call('Hardware', 'getSoftwareComponents', id=hardware_id)

    def create_credential(self, template):
        """Create a password for a software component"""
        return self.client.call('SoftLayer_Software_Component_Password', 'createObject', template)

    def remove_notification(self, identifier):
        """Remove a user hardware notification entry"""

        template = [{'id': identifier}]
        return self.client.call('SoftLayer_User_Customer_Notification_Hardware', 'deleteObjects', template)


def _get_bandwidth_key(items, hourly=True, no_public=False, location=None):
    """Picks a valid Bandwidth Item, returns the KeyName"""

    keyName = None
    # Prefer pay-for-use data transfer with hourly
    for item in items:

        capacity = float(item.get('capacity', 0))
        # Hourly and private only do pay-as-you-go bandwidth
        if any([utils.lookup(item, 'itemCategory', 'categoryCode') != 'bandwidth',
                (hourly or no_public) and capacity != 0.0,
                not (hourly or no_public) and capacity == 0.0]):
            continue

        keyName = item['keyName']
        for price in item['prices']:
            if not _matches_billing(price, hourly):
                continue
            if not _matches_location(price, location):
                continue
            return keyName

    raise SoftLayerError("Could not find valid price for bandwidth option")


def _get_port_speed_key(items, port_speed, no_public, location):
    """Choose a valid price id for port speed."""

    keyName = None
    for item in items:
        if utils.lookup(item, 'itemCategory', 'categoryCode') != 'port_speed':
            continue

        # Check for correct capacity and if the item matches private only
        if any([int(utils.lookup(item, 'capacity')) != port_speed,
                _is_private_port_speed_item(item) != no_public,
                not _is_bonded(item)]):
            continue
        keyName = item['keyName']
        for price in item['prices']:
            if not _matches_location(price, location):
                continue

            return keyName

    raise SoftLayerError("Could not find valid price for port speed: '%s'" % port_speed)


def _matches_billing(price, hourly):
    """Return True if the price object is hourly and/or monthly."""
    return any([hourly and price.get('hourlyRecurringFee') is not None,
                not hourly and price.get('recurringFee') is not None])


def _matches_location(price, location):
    """Return True if the price object matches the location."""
    # the price has no location restriction
    if not price.get('locationGroupId'):
        return True

    # Check to see if any of the location groups match the location group
    # of this price object
    for group in location['location']['location']['priceGroups']:
        if group['id'] == price['locationGroupId']:
            return True

    return False


def _is_private_port_speed_item(item):
    """Determine if the port speed item is private network only."""
    for attribute in item['attributes']:
        if attribute['attributeTypeKeyName'] == 'IS_PRIVATE_NETWORK_ONLY':
            return True

    return False


def _is_bonded(item):
    """Determine if the item refers to a bonded port."""
    for attribute in item['attributes']:
        if attribute['attributeTypeKeyName'] == 'NON_LACP':
            return False

    return True


def _get_location(package, location):
    """Get the longer key with a short location name."""
    for region in package['regions']:
        if region['location']['location']['name'] == location:
            return region

    raise SoftLayerError("Could not find valid location for: '%s'" % location)


def _get_preset_cost(preset, items, type_cost, location_group_id=None):
    """Get the preset cost.

    :param preset list: SoftLayer_Product_Package_Preset[]
    :param items list: SoftLayer_Product_Item[]
    :param type_cost string: 'hourly' or 'monthly'
    :param location_group_id int: locationGroupId's to get price for.
    """

    # Location based pricing on presets is a huge pain. Requires a few steps
    # 1. Get the presets prices, which are only ever the default prices
    # 2. Get that prices item ID, and use that to match the packages item
    # 3. find the package item, THEN find that items prices
    # 4. from those item prices, find the one that matches your locationGroupId

    item_cost = 0.00
    if type_cost == 'hourly':
        cost_key = 'hourlyRecurringFee'
    else:
        cost_key = 'recurringFee'
    for price in preset.get('prices', []):
        # Need to find the location specific price
        if location_group_id:
            # Find the item in the packages item list
            item_cost = find_item_in_package(cost_key, items, location_group_id, price)
        else:
            item_cost += float(price.get(cost_key))
    return item_cost


def find_item_in_package(cost_key, items, location_group_id, price):
    """Find the item in the packages item list.

    Will return the item cost.

    :param string cost_key: item cost key hourlyRecurringFee or recurringFee.
    :param list items: items list.
    :param int location_group_id: locationGroupId's to get price for.
    :param price: price data.
    """
    item_cost = 0.00
    for item in items:
        # Same item as the price's item
        if item.get('id') == price.get('itemId'):
            # Find the items location specific price.
            for location_price in item.get('prices', []):
                if location_price.get('locationGroupId', 0) == location_group_id:
                    item_cost += float(location_price.get(cost_key))
    return item_cost


def get_item_price(prices, location_group_id=None):
    """Get item prices, optionally for a specific location.

    Will return the default pricing information if there isn't any location specific pricing.

    :param prices list: SoftLayer_Product_Item_Price[]
    :param location_group_id int: locationGroupId's to get price for.
    """
    prices_list = []
    location_price = []
    for price in prices:
        # Only look up location prices if we need to
        if location_group_id:
            if price['locationGroupId'] == location_group_id:
                location_price.append(price)
        # Always keep track of default prices
        if not price['locationGroupId']:
            prices_list.append(price)

    # If this item has location specific pricing, return that
    if location_price:
        return location_price

    # Otherwise reutrn the default price list.
    return prices_list
