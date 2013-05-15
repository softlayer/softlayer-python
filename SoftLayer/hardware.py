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

    def list_hardware(self, hostname=None, public_ip=None, private_ip=None,
                      **kwargs):
        """ List all hardware.

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
        if hostname:
            _filter['hardware']['hostname'] = query_filter(hostname)

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

        return self.hardware.reloadCurrentOperatingSystemConfiguration(id=id,
            token='FORCE')

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
