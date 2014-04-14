"""
    SoftLayer.hardware
    ~~~~~~~~~~~~~~~~~~
    Hardware Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
# Invalid names are ignored due to long method names and short argument names
# pylint: disable=C0103
import socket
from SoftLayer.utils import NestedDict, query_filter, IdentifierMixin


class HardwareManager(IdentifierMixin, object):
    """
    Manages hardware devices.

    :param SoftLayer.API.Client client: an API client instance
    """

    def __init__(self, client):
        self.client = client
        self.hardware = self.client['Hardware_Server']
        self.account = self.client['Account']
        self.resolvers = [self._get_ids_from_ip, self._get_ids_from_hostname]

    def cancel_hardware(self, hardware_id, reason='unneeded', comment=''):
        """ Cancels the specified dedicated server.

        :param int hardware_id: The ID of the hardware to be cancelled.
        :param string reason: The reason code for the cancellation. This should
                              come from :func:`get_cancellation_reasons`.
        :param string comment: An optional comment to include with the
                               cancellation.
        """
        # Check to see if this is actually a pre-configured server (BMC). They
        # require a different cancellation call.
        server = self.get_hardware(hardware_id,
                                   mask='id,bareMetalInstanceFlag')

        if server.get('bareMetalInstanceFlag'):
            return self.cancel_metal(hardware_id)

        reasons = self.get_cancellation_reasons()
        cancel_reason = reasons['unneeded']

        if reason in reasons:
            cancel_reason = reasons[reason]

        # Arguments per SLDN:
        # attachmentId - Hardware ID
        # Reason
        # content - Comment about the cancellation
        # cancelAssociatedItems
        # attachmentType - Only option is HARDWARE
        return self.client['Ticket'].createCancelServerTicket(hardware_id,
                                                              cancel_reason,
                                                              comment,
                                                              True,
                                                              'HARDWARE')

    def cancel_metal(self, hardware_id, immediate=False):
        """ Cancels the specified bare metal instance.

        :param int id: The ID of the bare metal instance to be cancelled.
        :param bool immediate: If true, the bare metal instance will be
                               cancelled immediately. Otherwise, it will be
                               scheduled to cancel on the anniversary date.
        """
        hw_billing = self.get_hardware(hardware_id,
                                       mask='mask[id, billingItem.id]')

        billing_id = hw_billing['billingItem']['id']

        billing_item = self.client['Billing_Item']

        if immediate:
            return billing_item.cancelService(id=billing_id)
        else:
            return billing_item.cancelServiceOnAnniversaryDate(id=billing_id)

    def list_hardware(self, tags=None, cpus=None, memory=None, hostname=None,
                      domain=None, datacenter=None, nic_speed=None,
                      public_ip=None, private_ip=None, **kwargs):
        """ List all hardware (servers and bare metal computing instances).

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
            hw_items = set([
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
            ])
            server_items = set([
                'activeTransaction[id, transactionStatus[friendlyName,name]]',
            ])

            kwargs['mask'] = '[mask[%s],' \
                             ' mask(SoftLayer_Hardware_Server)[%s]]' % \
                             (','.join(hw_items),
                              ','.join(server_items))

        _filter = NestedDict(kwargs.get('filter') or {})
        if tags:
            _filter['hardware']['tagReferences']['tag']['name'] = {
                'operation': 'in',
                'options': [{'name': 'data', 'value': tags}],
            }

        if cpus:
            _filter['hardware']['processorPhysicalCoreAmount'] = \
                query_filter(cpus)

        if memory:
            _filter['hardware']['memoryCapacity'] = query_filter(memory)

        if hostname:
            _filter['hardware']['hostname'] = query_filter(hostname)

        if domain:
            _filter['hardware']['domain'] = query_filter(domain)

        if datacenter:
            _filter['hardware']['datacenter']['name'] = \
                query_filter(datacenter)

        if nic_speed:
            _filter['hardware']['networkComponents']['maxSpeed'] = \
                query_filter(nic_speed)

        if public_ip:
            _filter['hardware']['primaryIpAddress'] = \
                query_filter(public_ip)

        if private_ip:
            _filter['hardware']['primaryBackendIpAddress'] = \
                query_filter(private_ip)

        kwargs['filter'] = _filter.to_dict()
        return self.account.getHardware(**kwargs)

    def get_bare_metal_create_options(self):
        """ Retrieves the available options for creating a bare metal server.

        :returns: A dictionary of creation options. The categories to order are
                  contained within the 'categories' key. See
                  :func:`_parse_package_data` for detailed information.

        .. note::

           The information for ordering bare metal instances comes from
           multiple API calls. In order to make the process easier, this
           function will make those calls and reformat the results into a
           dictionary that's easier to manage. It's recommended that you cache
           these results with a reasonable lifetime for performance reasons.
        """
        hw_id = self.get_bare_metal_package_id()

        if not hw_id:
            return None

        return self._parse_package_data(hw_id)

    def get_bare_metal_package_id(self):
        """ Return the bare metal package id """
        packages = self.client['Product_Package'].getAllObjects(
            mask='mask[id, name]',
            filter={'name': query_filter('Bare Metal Instance')})

        hw_id = 0
        for package in packages:
            if 'Bare Metal Instance' == package['name']:
                hw_id = package['id']
                break

        return hw_id

    def get_available_dedicated_server_packages(self):
        """ Retrieves a list of packages that are available for ordering
        dedicated servers.

        :returns: A list of tuples of available dedicated server packages in
                  the form (id, name, description)
        """

        package_obj = self.client['Product_Package']
        packages = []

        # Pull back only server packages
        mask = 'id,name,description,type'
        _filter = {
            'type': {
                'keyName': {
                    'operation': 'in',
                    'options': [
                        {'name': 'data',
                         'value': ['BARE_METAL_CPU', 'BARE_METAL_CORE']}
                    ],
                },
            },
        }

        for package in package_obj.getAllObjects(mask=mask, filter=_filter):
            # Filter out packages without a name or that are designated as
            # 'OUTLET.' The outlet packages are missing some necessary data
            # and their orders will fail.
            if package.get('name') and 'OUTLET' not in package['description']:
                packages.append((package['id'], package['name'],
                                 package['description']))

        return packages

    def get_dedicated_server_create_options(self, package_id):
        """ Retrieves the available options for creating a dedicated server in
        a specific chassis (based on package ID).

        :param int package_id: The package ID to retrieve the creation options
                               for. This should come from
                               :func:`get_available_dedicated_server_packages`.
        :returns: A dictionary of creation options. The categories to order are
                  contained within the 'categories' key. See
                  :func:`_parse_package_data` for detailed information.

        .. note::

           The information for ordering dedicated servers comes from multiple
           API calls. In order to make the process simpler, this function will
           make those calls and reformat the results into a dictionary that's
           easier to manage. It's recommended that you cache these results with
           a reasonable lifetime for performance reasons.
        """
        return self._parse_package_data(package_id)

    def get_hardware(self, hardware_id, **kwargs):
        """ Get details about a hardware device

        :param integer id: the hardware ID
        :returns: A dictionary containing a large amount of information about
                  the specified server.

        """

        if 'mask' not in kwargs:
            items = set([
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
                'networkComponents[id, status, speed, maxSpeed, name,'
                'ipmiMacAddress, ipmiIpAddress, macAddress, primaryIpAddress,'
                'port, primarySubnet]',
                'networkComponents.primarySubnet[id, netmask,'
                'broadcastAddress, networkIdentifier, gateway]',
                'hardwareChassis[id,name]',
                'activeTransaction[id, transactionStatus[friendlyName,name]]',
                'operatingSystem.softwareLicense.'
                'softwareDescription[manufacturer,name,version,referenceCode]',
                'operatingSystem.passwords[username,password]',
                'billingItem.recurringFee',
                'hourlyBillingFlag',
                'tagReferences[id,tag[name,id]]',
                'networkVlans[id,vlanNumber,networkSpace]',
            ])
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        return self.hardware.getObject(id=hardware_id, **kwargs)

    def reload(self, hardware_id, post_uri=None, ssh_keys=None):
        """ Perform an OS reload of a server with its current configuration.

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

    def change_port_speed(self, hardware_id, public, speed):
        """ Allows you to change the port speed of a server's NICs.

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
        """ Places an order for a piece of hardware.

        Translates a list of arguments into a dictionary necessary for creating
        a server.

        .. warning::
           All items here must be price IDs, NOT quantities!

        :param int server: The identification string for the server to
                           order. This will either be the CPU/Memory
                           combination ID for bare metal instances or the
                           CPU model for dedicated servers.
        :param string hostname: The hostname to use for the new server.
        :param string domain: The domain to use for the new server.
        :param bool hourly: Flag to indicate if this server should be billed
                            hourly (default) or monthly. Only applies to bare
                            metal instances.
        :param string location: The location string (data center) for the
                                server
        :param int os: The operating system to use
        :param array disks: An array of disks for the server. Disks will be
                            added in the order specified.
        :param int port_speed: The port speed for the server.
        :param bool bare_metal: Flag to indicate if this is a bare metal server
                                or a dedicated server (default).
        :param int ram: The amount of RAM to order. Only applies to dedicated
                        servers.
        :param int package_id: The package_id to use for the server. This
                               should either be a chassis ID for dedicated
                               servers or the bare metal instance package ID,
                               which can be obtained by calling
                               get_bare_metal_package_id
        :param int disk_controller: The disk controller to use.
        :param list ssh_keys: The SSH keys to add to the root user
        :param int public_vlan: The ID of the public VLAN on which you want
                                this server placed.
        :param int private_vlan: The ID of the public VLAN on which you want
                                 this server placed.
        :param string post_uri: The URI of the post-install script to run
                                after reload

        .. warning::
           Due to how the ordering structure currently works, all ordering
           takes place using price IDs rather than quantities. See the
           following sample for an example of using HardwareManager functions
           for ordering a basic server.

        ::

           # client is assumed to be an initialized SoftLayer.API.Client object
           mgr = HardwareManager(client)

           # Package ID 32 corresponds to the 'Quad Processor, Quad Core Intel'
           # package. This information can be obtained from the
           # :func:`get_available_dedicated_server_packages` function.
           options = mgr.get_dedicated_server_create_options(32)

           # Review the contents of options to find the information that
           # applies to your order. For the sake of this example, we assume
           # that your selections are a series of item IDs for each category
           # organized into a key-value dictionary.

           # This contains selections for all required categories
           selections = {
               'server': 542, # Quad Processor Quad Core Intel 7310 - 1.60GHz
               'pri_ip_addresses': 15, # 1 IP Address
               'notification': 51, # Email and Ticket
               'ram': 280, # 16 GB FB-DIMM Registered 533/667
               'bandwidth': 173, # 5000 GB Bandwidth
               'lockbox': 45, # 1 GB Lockbox
               'monitoring': 49, # Host Ping
               'disk0': 14, # 500GB SATA II (for the first disk)
               'response': 52, # Automated Notification
               'port_speed': 187, # 100 Mbps Public & Private Networks
               'power_supply': 469, # Redundant Power Supplies
               'disk_controller': 487, # Non-RAID
               'vulnerability_scanner': 307, # Nessus
               'vpn_management': 309, # Unlimited SSL VPN Users
               'remote_management': 504, # Reboot / KVM over IP
               'os': 4166, # Ubuntu Linux 12.04 LTS Precise Pangolin (64 bit)
           }

           args = {
               'location': 'FIRST_AVAILABLE', # Pick the first available DC
               'packageId': 32, # From above
               'disks': [],
           }

           for cat, item_id in selections:
               for item in options['categories'][cat]['items'].items():
                   if item['id'] == item_id:
                       if 'disk' not in cat or 'disk_controller' == cat:
                           args[cat] = item['price_id']
                       else:
                           args['disks'].append(item['price_id'])

           # You can call :func:`verify_order` here to test the order instead
           # of actually placing it if you prefer.
           result = mgr.place_order(**args)

        """
        create_options = self._generate_create_dict(**kwargs)
        return self.client['Product_Order'].placeOrder(create_options)

    def verify_order(self, **kwargs):
        """ Verifies an order for a piece of hardware without actually placing
        it. See :func:`place_order` for a list of available options.
        """
        create_options = self._generate_create_dict(**kwargs)
        return self.client['Product_Order'].verifyOrder(create_options)

    def get_cancellation_reasons(self):
        """
        Returns a dictionary of valid cancellation reasons that can be used
        when cancelling a dedicated server via :func:`cancel_hardware`.
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

    def _generate_create_dict(
            self, server=None, hostname=None, domain=None, hourly=False,
            location=None, os=None, disks=None, port_speed=None,
            bare_metal=None, ram=None, package_id=None, disk_controller=None,
            ssh_keys=None, public_vlan=None, private_vlan=None, post_uri=None):
        """
        Translates a list of arguments into a dictionary necessary for creating
        a server.

        .. warning::
           All items here must be price IDs, NOT quantities!

        :param int server: The identification string for the server to
                           order. This will either be the CPU/Memory
                           combination ID for bare metal instances or the
                           CPU model for dedicated servers.
        :param string hostname: The hostname to use for the new server.
        :param string domain: The domain to use for the new server.
        :param bool hourly: Flag to indicate if this server should be billed
                            hourly (default) or monthly. Only applies to bare
                            metal instances.
        :param string location: The location string (data center) for the
                                server
        :param int os: The operating system to use
        :param array disks: An array of disks for the server. Disks will be
                            added in the order specified.
        :param int port_speed: The port speed for the server.
        :param bool bare_metal: Flag to indicate if this is a bare metal server
                                or a dedicated server (default).
        :param int ram: The amount of RAM to order. Only applies to dedicated
                        servers.
        :param int package_id: The package_id to use for the server. This
                               should either be a chassis ID for dedicated
                               servers or the bare metal instance package ID,
                               which can be obtained by calling
                               get_bare_metal_package_id
        :param int disk_controller: The disk controller to use.
        :param list ssh_keys: The SSH keys to add to the root user
        :param int public_vlan: The ID of the public VLAN on which you want
                                this server placed.
        :param int private_vlan: The ID of the public VLAN on which you want
                                 this server placed.
        """
        arguments = ['server', 'hostname', 'domain', 'location', 'os', 'disks',
                     'port_speed', 'bare_metal', 'ram', 'package_id',
                     'disk_controller', 'server_core', 'disk0']

        hardware = {
            'bareMetalInstanceFlag': bare_metal,
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
            'location': location,
            'prices': [],
        }

        if post_uri:
            order['provisionScripts'] = [post_uri]

        if ssh_keys:
            order['sshKeys'] = [{'sshKeyIds': ssh_keys}]

        if bare_metal:
            order['packageId'] = self.get_bare_metal_package_id()
            order['prices'].append({'id': int(server)})
            p_options = self.get_bare_metal_create_options()
            if hourly:
                order['useHourlyPricing'] = True
        else:
            order['packageId'] = package_id
            order['prices'].append({'id': int(server)})
            p_options = self.get_dedicated_server_create_options(package_id)

        if disks:
            for disk in disks:
                order['prices'].append({'id': int(disk)})

        if os:
            order['prices'].append({'id': int(os)})

        if port_speed:
            order['prices'].append({'id': int(port_speed)})

        if ram:
            order['prices'].append({'id': int(ram)})

        if disk_controller:
            order['prices'].append({'id': int(disk_controller)})

        # Find all remaining required categories so we can auto-default them
        required_fields = []
        for category, data in p_options['categories'].items():
            if data.get('is_required') and category not in arguments:
                if 'disk' in category:
                    # This block makes sure that we can default unspecified
                    # disks if the user hasn't specified enough.
                    disk_count = int(category.replace('disk', ''))
                    if len(disks) >= disk_count + 1:
                        continue
                required_fields.append(category)

        for category in required_fields:
            price = get_default_value(p_options, category, hourly=hourly)
            order['prices'].append({'id': price})

        return order

    def _get_ids_from_hostname(self, hostname):
        """ Returns list of matching hardware IDs for a given hostname """
        results = self.list_hardware(hostname=hostname, mask="id")
        return [result['id'] for result in results]

    def _get_ids_from_ip(self, ip):
        """ Returns list of matching hardware IDs for a given ip address """
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

    def _parse_package_data(self, package_id):
        """
        Parses data from the specified package into a consistent dictionary.

        The data returned by the API varies significantly from one package
        to another, which means that consuming it can make your program more
        complicated than desired. This function will make all necessary API
        calls for the specified package ID and build the results into a
        consistently formatted dictionary like so:

        result = {
            'locations': [{'delivery_information': <string>,
                           'keyname': <string>,
                           'long_name': <string>}],
            'categories': {
                'category_code': {
                    'sort': <int>,
                    'step': <int>,
                    'is_required': <bool>,
                    'name': <string>,
                    'group': <string>,
                    'items': [
                        {
                            'id': <int>,
                            'description': <string>,
                            'sort': <int>,
                            'price_id': <int>,
                            'recurring_fee': <float>,
                            'setup_fee': <float>,
                            'hourly_recurring_fee': <float>,
                            'one_time_fee': <float>,
                            'labor_fee': <float>,
                            'capacity': <float>,
                        }
                    ]
                }
            }
        }

        Your code can rely upon each of those elements always being present.
        Each list will contain at least one entry as well, though most will
        contain more than one.
        """
        package = self.client['Product_Package']

        results = {
            'categories': {},
            'locations': []
        }

        # First pull the list of available locations. We do it with the
        # getObject() call so that we get access to the delivery time info.
        object_data = package.getRegions(id=package_id)

        for loc in object_data:
            details = loc['location']['locationPackageDetails'][0]

            results['locations'].append({
                'delivery_information': details.get('deliveryTimeInformation'),
                'keyname': loc['keyname'],
                'long_name': loc['description'],
            })

        mask = 'mask[itemCategory[group]]'

        for config in package.getConfiguration(id=package_id, mask=mask):
            code = config['itemCategory']['categoryCode']
            group = NestedDict(config['itemCategory']) or {}
            category = {
                'sort': config['sort'],
                'step': config['orderStepId'],
                'is_required': config['isRequired'],
                'name': config['itemCategory']['name'],
                'group': group['group']['name'],
                'items': [],
            }

            results['categories'][code] = category

        # Now pull in the available package item
        for category in package.getCategories(id=package_id):
            code = category['categoryCode']
            items = []

            for group in category['groups']:
                for price in group['prices']:
                    items.append({
                        'id': price['itemId'],
                        'description': price['item']['description'],
                        'sort': price['sort'],
                        'price_id': price['id'],
                        'recurring_fee': price.get('recurringFee'),
                        'setup_fee': price.get('setupFee'),
                        'hourly_recurring_fee':
                        price.get('hourlyRecurringFee'),
                        'one_time_fee': price.get('oneTimeFee'),
                        'labor_fee': price.get('laborFee'),
                        'capacity': float(price['item'].get('capacity', 0)),
                    })
            results['categories'][code]['items'] = items

        return results

    def edit(self, hardware_id, userdata=None, hostname=None, domain=None,
             notes=None):
        """ Edit hostname, domain name, notes, and/or the user data of the
        hardware

        Parameters set to None will be ignored and not attempted to be updated.

        :param integer hardware_id: the instance ID to edit
        :param string userdata: user data on the hardware to edit.
                                If none exist it will be created
        :param string hostname: valid hostname
        :param string domain: valid domain namem
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


def get_default_value(package_options, category, hourly=False):
    """ Returns the default price ID for the specified category.

    This determination is made by parsing the items in the package_options
    argument and finding the first item that has zero specified for every fee
    field.

    .. note::
       If the category has multiple items with no fee, this will return the
       first it finds and then short circuit. This may not match the default
       value presented on the SoftLayer ordering portal. Additionally, this
       method will return None if there are no free items in the category.

    :returns: Returns the price ID of the first free item it finds or None
              if there are no free items.
    """
    if category not in package_options['categories']:
        return

    for item in package_options['categories'][category]['items']:
        if hourly:
            if item.get('hourly_recurring_fee') is None:
                continue
        else:
            if item.get('recurring_fee') is None:
                continue

        if not any([float(item.get('setup_fee') or 0),
                    float(item.get('recurring_fee') or 0),
                    float(item.get('hourly_recurring_fee') or 0),
                    float(item.get('one_time_fee') or 0),
                    float(item.get('labor_fee') or 0)]):
            return item['price_id']
