"""
    SoftLayer.hardware
    ~~~~~~~~~~~~~~~~~~
    Hardware Manager/helpers

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""

import socket
from SoftLayer.utils import NestedDict, query_filter, IdentifierMixin


class HardwareManager(IdentifierMixin, object):
    """ Manages hardware devices. """

    def __init__(self, client):
        """ HardwareManager initialization.

        :param SoftLayer.API.Client client: an API client instance

        """
        self.client = client
        self.hardware = self.client['Hardware_Server']
        self.account = self.client['Account']
        self.resolvers = [self._get_ids_from_ip, self._get_ids_from_hostname]

    def cancel_hardware(self, id, reason='unneeded', comment=''):
        """ Cancels the specified dedicated server.

        :param int id: The ID of the hardware to be cancelled.
        :param bool immediate: If true, the hardware will be cancelled
                               immediately. Otherwise, it will be
                               scheduled to cancel on the anniversary date.
        :param string reason: The reason code for the cancellation.
        """

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
        ticket_obj = self.client['Ticket']
        return ticket_obj.createCancelServerTicket(id, cancel_reason,
                                                   comment, True,
                                                   'HARDWARE')

    def cancel_metal(self, id, immediate=False):
        """ Cancels the specified bare metal instance.

        :param int id: The ID of the bare metal instance to be cancelled.
        :param bool immediate: If true, the bare metal instance will be
                               cancelled immediately. Otherwise, it will be
                               scheduled to cancel on the anniversary date.
        """
        hw_billing = self.get_hardware(id=id,
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
        """ List all hardware.

        :param list tags: filter based on tags
        :param integer cpus: filter based on number of CPUS
        :param integer memory: filter based on amount of memory in gigabytes
        :param string hostname: filter based on hostname
        :param string domain: filter based on domain
        :param string datacenter: filter based on datacenter
        :param integer nic_speed: filter based on network speed (in MBPS)
        :param string public_ip: filter based on public ip address
        :param string private_ip: filter based on private ip address
        :param dict \*\*kwargs: response-level arguments (limit, offset, etc.)

        """
        if 'mask' not in kwargs:
            items = set([
                'id',
                'hostname',
                'domain',
                'hardwareStatusId',
                'globalIdentifier',
                'fullyQualifiedDomainName',
                'processorCoreAmount',
                'memoryCapacity',
                'primaryBackendIpAddress',
                'primaryIpAddress',
                'datacenter.name',
            ])
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        _filter = NestedDict(kwargs.get('filter') or {})
        if tags:
            _filter['hardware']['tagReferences']['tag']['name'] = {
                'operation': 'in',
                'options': [{'name': 'data', 'value': tags}],
            }

        if cpus:
            _filter['hardware']['processorCoreAmount'] = query_filter(cpus)

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

        The information for ordering bare metal instances comes from multiple
        API calls. In order to make the process easier, this function will
        make those calls and reformat the results into a dictionary that's
        easier to manage. It's recommended that you cache these results with a
        reasonable lifetime for performance reasons.
        """
        hw_id = self._get_bare_metal_package_id()

        if not hw_id:
            return None

        return self._parse_package_data(hw_id)

    def get_available_dedicated_server_packages(self):
        """ Retrieves a list of packages that are available for ordering
        dedicated servers.

        Note - This currently returns a hard coded list until the API is
        updated to allow filtering on packages to just those for ordering
        servers.
        """
        package_ids = [13, 15, 23, 25, 26, 27, 29, 32, 41, 42, 43, 44, 49, 51,
                       52, 53, 54, 55, 56, 57, 126, 140, 141, 142, 143, 144,
                       145, 146, 147, 148, 158]

        package_obj = self.client['Product_Package']
        packages = []

        for package_id in package_ids:
            package = package_obj.getObject(id=package_id,
                                            mask='mask[id, name, description]')

            if (package.get('name')):
                packages.append((package['id'], package['name'],
                                 package['description']))

        return packages

    def get_dedicated_server_create_options(self, package_id):
        """ Retrieves the available options for creating a dedicated server in
        a specific chassis (based on package ID).

        The information for ordering dedicated servers comes from multiple
        API calls. In order to make the process easier, this function will
        make those calls and reformat the results into a dictionary that's
        easier to manage. It's recommended that you cache these results with a
        reasonable lifetime for performance reasons.
        """
        return self._parse_package_data(package_id)

    def get_hardware(self, id, **kwargs):
        """ Get details about a hardware device

        :param integer id: the hardware ID

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
                'processorCoreAmount',
                'memoryCapacity',
                'notes',
                'primaryBackendIpAddress',
                'primaryIpAddress',
                'datacenter.name',
                'networkComponents[id, status, speed, maxSpeed, name,'
                'ipmiMacAddress, ipmiIpAddress, macAddress, primaryIpAddress,'
                'port, primarySubnet]',
                'networkComponents.primarySubnet[id, netmask,'
                'broadcastAddress, networkIdentifier, gateway]',
                'activeTransaction.id',
                'operatingSystem.softwareLicense.'
                'softwareDescription[manufacturer,name,version,referenceCode]',
                'operatingSystem.passwords[username,password]',
                'billingItem.recurringFee',
                'tagReferences[id,tag[name,id]]',
            ])
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        return self.hardware.getObject(id=id, **kwargs)

    def reload(self, id, post_uri=None):
        """ Perform an OS reload of a server with its current configuration.

        :param integer id: the instance ID to reload
        :param string post_url: The URI of the post-install script to run
                                after reload

        """

        payload = {
            'token': 'FORCE',
            'config': {},
        }

        if post_uri:
            payload['config']['customProvisionScriptUri'] = post_uri

        return self.hardware.reloadOperatingSystem('FORCE', payload['config'],
                                                   id=id)

    def change_port_speed(self, id, public, speed):
        """ Allows you to change the port speed of a server's NICs.

        :param int id: The ID of the server
        :param bool public: Flag to indicate which interface to change.
                           True (default) means the public interface.
                           False indicates the private interface.
        :param int speed: The port speed to set.
        """
        if public:
            func = self.hardware.setPublicNetworkInterfaceSpeed
        else:
            func = self.hardware.setPrivateNetworkInterfaceSpeed

        return func(speed, id=id)

    def place_order(self, **kwargs):
        """ Places an order for a piece of hardware. See _generate_create_dict
        for a list of available options.
        """
        create_options = self._generate_create_dict(**kwargs)
        return self.client['Product_Order'].placeOrder(create_options)

    def verify_order(self, **kwargs):
        """ Verifies an order for a piece of hardware without actually placing
        it. See _generate_create_dict for a list of available options.
        """
        create_options = self._generate_create_dict(**kwargs)
        return self.client['Product_Order'].verifyOrder(create_options)

    def get_cancellation_reasons(self):
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
            bare_metal=None, ram=None, package_id=None, disk_controller=None):
        """
        Translates a list of arguments into a dictionary necessary for creating
        a server. NOTE - All items here must be price IDs, NOT quantities!

        :param string server: The identification string for the server to
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
                               _get_bare_metal_package_id
        :param int disk_controller: The disk controller to use.
        """
        arguments = ['server', 'hostname', 'domain', 'location', 'os', 'disks',
                     'port_speed', 'bare_metal', 'ram', 'package_id',
                     'disk_controller', 'server_core', 'disk0']

        order = {
            'hardware': [{
                'bareMetalInstanceFlag': bare_metal,
                'hostname': hostname,
                'domain': domain,
            }],
            'location': location,
            'prices': [
            ],
        }

        if bare_metal:
            order['packageId'] = self._get_bare_metal_package_id()
            order['prices'].append({'id': int(server)})
            p_options = self.get_bare_metal_create_options()
            if hourly:
                order['hourlyBillingFlag'] = True
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
        for category, data in p_options['categories'].iteritems():
            if data.get('is_required') and category not in arguments:
                required_fields.append(category)

        for category in required_fields:
            price = get_default_value(p_options, category)
            order['prices'].append({'id': price})

        return order

    def _get_bare_metal_package_id(self):
        packages = self.client['Product_Package'].getAllObjects(
            mask='mask[id, name]',
            filter={'name': query_filter('Bare Metal Instance')})

        hw_id = 0
        for package in packages:
            if 'Bare Metal Instance' == package['name']:
                hw_id = package['id']
                break

        return hw_id

    def _get_ids_from_hostname(self, hostname):
        results = self.list_hardware(hostname=hostname, mask="id")
        return [result['id'] for result in results]

    def _get_ids_from_ip(self, ip):
        try:
            # Does it look like an ip address?
            socket.inet_aton(ip)
        except socket.error:
            return []

        # Find the CCI via ip address. First try public ip, then private
        results = self.list_hardware(public_ip=ip, mask="id")
        if results:
            return [result['id'] for result in results]

        results = self.list_hardware(private_ip=ip, mask="id")
        if results:
            return [result['id'] for result in results]

    def _parse_package_data(self, id):
        package = self.client['Product_Package']

        results = {
            'categories': {},
            'locations': []
        }

        # First pull the list of available locations. We do it with the
        # getObject() call so that we get access to the delivery time info.
        object_data = package.getRegions(id=id)

        for loc in object_data:
            details = loc['location']['locationPackageDetails'][0]

            results['locations'].append({
                'delivery_information': details.get('deliveryTimeInformation'),
                'keyname': loc['keyname'],
                'long_name': loc['description'],
            })

        mask = 'mask[itemCategory[group]]'

        for config in package.getConfiguration(id=id, mask=mask):
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
        for item in package.getItems(id=id, mask='mask[itemCategory]'):
            category_code = item['itemCategory']['categoryCode']

            if category_code not in results['categories']:
                results['categories'][category_code] = {'name': category_code,
                                                        'items': []}
            results['categories'][category_code]['items'].append({
                'id': item['id'],
                'description': item['description'],
                'prices': item['prices'],
                'sort': item['prices'][0]['sort'],
                'price_id': item['prices'][0]['id'],
                'recurring_fee': float(item['prices'][0].get('recurringFee',
                                                             0)),
                'capacity': float(item.get('capacity', 0)),
            })

        return results


def get_default_value(package_options, category):
    if category not in package_options['categories']:
        return

    for item in package_options['categories'][category]['items']:
        if not any([
            float(item['prices'][0].get('setupFee', 0)),
            float(item['prices'][0].get('recurringFee', 0)),
            float(item['prices'][0].get('hourlyRecurringFee', 0)),
            float(item['prices'][0].get('oneTimeFee', 0)),
            float(item['prices'][0].get('laborFee', 0)),
        ]):
            return item['price_id']
