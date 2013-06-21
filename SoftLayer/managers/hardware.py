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

        if reason in reasons:
            reason = reasons[reason]
        else:
            reason = reasons['unneeded']

        # Arguments per SLDN:
        # attachmentId - Hardware ID
        # Reason
        # content - Comment about the cancellation
        # cancelAssociatedItems
        # attachmentType - Only option is HARDWARE
        return self.client['Ticket'].createCancelServerTicket(id, reason,
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

        package = self.client['Product_Package']

        results = {
            'categories': {},
            'locations': []
        }

        # First pull the list of available locations. We do it with the
        # getObject() call so that we get access to the delivery time info.
        object_data = package.getRegions(id=hw_id)

        for loc in object_data:
            details = loc['location']['locationPackageDetails'][0]

            results['locations'].append({
                'delivery_information': details.get('deliveryTimeInformation'),
                'keyname': loc['keyname'],
                'long_name': loc['description'],
            })

        for config in package.getConfiguration(id=hw_id,
                                               mask='mask[itemCategory]'):
            code = config['itemCategory']['categoryCode']
            category = {
                'sort': config['sort'],
                'step': config['orderStepId'],
                'is_required': config['isRequired'],
                'name': config['itemCategory']['name'],
                'items': [],
            }

            results['categories'][code] = category

        # Now pull in the available package item
        for item in package.getItems(id=hw_id, mask='mask[itemCategory]'):
            category_code = item['itemCategory']['categoryCode']

            if category_code not in results['categories']:
                results['categories'][category_code] = {'name': category_code,
                                                        'items': []}
            results['categories'][category_code]['items'].append({
                'id': item['id'],
                'description': item['description'],
                # TODO - Deal with multiple prices properly.
                'prices': item['prices'],
                'sort': item['prices'][0]['sort'],
                'price_id': item['prices'][0]['id'],
                'capacity': int(item.get('capacity') or 0),
            })

        return results

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
                'networkComponents[id, status, maxSpeed, name,'
                'ipmiMacAddress, ipmiIpAddress, macAddress,'
                'primaryIpAddress, port, primarySubnet]',
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

    def reload(self, id):
        """ Perform an OS reload of a server with its current configuration.

        :param integer id: the instance ID to reload

        """

        return self.hardware.reloadCurrentOperatingSystemConfiguration(
            'FORCE', id=id)

    def place_order(self, **kwargs):
        create_options = self._generate_create_dict(**kwargs)
        return self.client['Product_Order'].placeOrder(create_options)

    def verify_order(self, **kwargs):
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
            self, server_core=None, hourly=True,
            hostname=None, domain=None, disk0=None,
            location=None, os=None, image_id=None,
            pri_ip_addresses=None, bandwidth=None,
            userdata=None, monitoring=None, port_speed=None,
            vulnerability_scanner=None, response=None,
            vpn_management=None, remote_management=None,
            notification=None, bare_metal=True, database=None):

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

        if server_core:
            order['prices'].append({'id': int(server_core)})

        if disk0:
            order['prices'].append({'id': int(disk0)})

        if os:
            order['prices'].append({'id': int(os)})

        if pri_ip_addresses:
            order['prices'].append({'id': int(pri_ip_addresses)})

        if bandwidth:
            order['prices'].append({'id': int(bandwidth)})

        if monitoring:
            order['prices'].append({'id': int(monitoring)})

        if port_speed:
            order['prices'].append({'id': int(port_speed)})

        if vulnerability_scanner:
            order['prices'].append({'id': int(vulnerability_scanner)})

        if response:
            order['prices'].append({'id': int(response)})

        if vpn_management:
            order['prices'].append({'id': int(vpn_management)})

        if remote_management:
            order['prices'].append({'id': int(remote_management)})

        if notification:
            order['prices'].append({'id': int(notification)})

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
