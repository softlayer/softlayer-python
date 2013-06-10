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

    def list_hardware(self, tags=None, hostname=None, domain=None,
                      datacenter=None, nic_speed=None, public_ip=None,
                      private_ip=None, **kwargs):
        """ List all hardware.

        :param list tags: filter based on tags
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
                'networkComponents[id, status, maxSpeed, name,' \
                'ipmiMacAddress, ipmiIpAddress, macAddress, primaryIpAddress,'\
                'port, primarySubnet]',
                'networkComponents.primarySubnet[id, netmask,' \
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
