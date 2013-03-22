"""
    SoftLayer.CCI
    ~~~~~~~~~~~~~
    CCI Manager/helpers

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import socket

from SoftLayer.exceptions import SoftLayerError
from SoftLayer.utils import NestedDict, query_filter, IdentifierMixin


class CCICreateMissingRequired(SoftLayerError):
    def __init__(self):
        self.message = "cpu, memory, hostname, and domain are required"


class CCICreateMutuallyExclusive(SoftLayerError):
    def __init__(self, *args):
        self.message = "Can only specify one of:", ','.join(args)


class CCIManager(object, IdentifierMixin):
    """ Manage CCIs """
    def __init__(self, client):
        self.client = client
        self.account = client['Account']
        self.guest = client['Virtual_Guest']
        self.resolvers = [self._get_ids_from_ip, self._get_ids_from_hostname]

    def list_instances(self, hourly=True, monthly=True, tags=None, cpus=None,
                       memory=None, hostname=None, domain=None,
                       local_disk=None, datacenter=None, nic_speed=None,
                       public_ip=None, private_ip=None, **kwargs):
        """ Retrieve a list of all CCIs on the account.

        :param boolean hourly: include hourly instances
        :param boolean monthly: include monthly instances
        :param list tags: filter based on tags
        :param integer cpus: filter based on number of CPUS
        :param integer memory: filter based on amount of memory
        :param string hostname: filter based on hostname
        :param string domain: filter based on domain
        :param string local_disk: filter based on local_disk
        :param string datacenter: filter based on datacenter
        :param integer nic_speed: filter based on network speed (in MBPS)
        :param string public_ip: filter based on public ip address
        :param string private_ip: filter based on private ip address
        :param dict **kwargs: response-level arguments (limit, offset, etc.)

        """
        if 'mask' not in kwargs:
            items = set([
                'id',
                'globalIdentifier',
                'fullyQualifiedDomainName',
                'primaryBackendIpAddress',
                'primaryIpAddress',
                'lastKnownPowerState.name',
                'powerState.name',
                'maxCpu',
                'maxMemory',
                'datacenter.name',
                'activeTransaction.transactionStatus[friendlyName,name]',
                'status.name',
                'tagReferences[id,tag[name,id]]',
            ])
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        call = 'getVirtualGuests'
        if not all([hourly, monthly]):
            if hourly:
                call = 'getHourlyVirtualGuests'
            elif monthly:
                call = 'getMonthlyVirtualGuests'

        _filter = NestedDict(kwargs.get('filter') or {})
        if tags:
            _filter['virtualGuests']['tagReferences']['tag']['name'] = {
                'operation': 'in',
                'options': [{'name': 'data', 'value': tags}],
            }

        if cpus:
            _filter['virtualGuests']['maxCpu'] = query_filter(cpus)

        if memory:
            _filter['virtualGuests']['maxMemory'] = query_filter(memory)

        if hostname:
            _filter['virtualGuests']['hostname'] = query_filter(hostname)

        if domain:
            _filter['virtualGuests']['domain'] = query_filter(domain)

        if local_disk is not None:
            _filter['virtualGuests']['localDiskFlag'] = \
                query_filter(bool(local_disk))

        if datacenter:
            _filter['virtualGuests']['datacenter']['name'] = \
                query_filter(datacenter)

        if nic_speed:
            _filter['virtualGuests']['networkComponents']['maxSpeed'] = \
                query_filter(nic_speed)

        if public_ip:
            _filter['virtualGuests']['primaryIpAddress'] = \
                query_filter(public_ip)

        if private_ip:
            _filter['virtualGuests']['primaryBackendIpAddress'] = \
                query_filter(private_ip)

        kwargs['filter'] = _filter.to_dict()
        func = getattr(self.account, call)
        return func(**kwargs)

    def get_instance(self, id, **kwargs):
        """ Get details about a CCI instance

        :param integer id: the instance ID

        """
        if 'mask' not in kwargs:
            items = set([
                'id',
                'globalIdentifier',
                'fullyQualifiedDomainName',
                'hostname',
                'domain',
                'createDate',
                'modifyDate',
                'notes',
                'dedicatedAccountHostOnlyFlag',
                'privateNetworkOnlyFlag',
                'primaryBackendIpAddress',
                'primaryIpAddress',
                'lastKnownPowerState.name',
                'powerState.name',
                'maxCpu',
                'maxMemory',
                'datacenter.name',
                'activeTransaction.id',
                'blockDeviceTemplateGroup[id, name]',
                'status.name',
                'operatingSystem.softwareLicense.'
                'softwareDescription[manufacturer,name,version,referenceCode]',
                'operatingSystem.passwords[username,password]',
                'billingItem.recurringFee',
                'tagReferences[id,tag[name,id]]',
            ])
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        return self.guest.getObject(id=id, **kwargs)

    def get_create_options(self):
        return self.guest.getCreateObjectOptions()

    def cancel_instance(self, id):
        """ Cancel an instance immediately, deleting all its data.

        :param integer id: the instance ID to cancel

        """
        return self.guest.deleteObject(id=id)

    def reload_instance(self, id):
        """ Perform an OS reload of an instance with its current configuration.

        :param integer id: the instance ID to reload

        """
        return self.guest.reloadCurrentOperatingSystemConfiguration(id=id)

    def _generate_create_dict(
            self, cpus=None, memory=None, hourly=True,
            hostname=None, domain=None, local_disk=True,
            datacenter=None, os_code=None, image_id=None,
            private=False, public_vlan=None, private_vlan=None,
            userdata=None, nic_speed=None):

        required = [cpus, memory, hostname, domain]

        mutually_exclusive = [
            {'os_code': os_code, "image_id": image_id},
        ]

        if not all(required):
            raise CCICreateMissingRequired()

        for me in mutually_exclusive:
            if all(me.values()):
                raise CCICreateMutuallyExclusive(*me.keys())

        data = {
            "startCpus": int(cpus),
            "maxMemory": int(memory),
            "hostname": hostname,
            "domain": domain,
            "localDiskFlag": local_disk,
        }

        data["hourlyBillingFlag"] = hourly

        if private:
            data["dedicatedAccountHostOnlyFlag"] = private

        if image_id:
            data["blockDeviceTemplateGroup"] = {"globalIdentifier": image_id}
        elif os_code:
            data["operatingSystemReferenceCode"] = os_code

        if datacenter:
            data["datacenter"] = {"name": datacenter}

        if public_vlan:
            data.update({
                'primaryNetworkComponent': {
                    "networkVlan": {"id": int(public_vlan)}}})
        if private_vlan:
            data.update({
                "primaryBackendNetworkComponent": {
                    "networkVlan": {"id": int(private_vlan)}}})

        if userdata:
            data['userData'] = [{'value': userdata}, ]

        if nic_speed:
            data['networkComponents'] = [{'maxSpeed': nic_speed}]

        return data

    def verify_create_instance(self, **kwargs):
        """ see _generate_create_dict """  # TODO: document this
        create_options = self._generate_create_dict(**kwargs)
        return self.guest.generateOrderTemplate(create_options)

    def create_instance(self, **kwargs):
        """ see _generate_create_dict """  # TODO: document this
        create_options = self._generate_create_dict(**kwargs)
        return self.guest.createObject(create_options)

    def _get_ids_from_hostname(self, hostname):
        results = self.list_instances(hostname=hostname, mask="id")
        return [result['id'] for result in results]

    def _get_ids_from_ip(self, ip):
        try:
            # Does it look like an ip address?
            socket.inet_aton(ip)
        except socket.error:
            return []

        # Find the CCI via ip address. First try public ip, then private
        results = self.list_instances(public_ip=ip, mask="id")
        if results:
            return [result['id'] for result in results]

        results = self.list_instances(private_ip=ip, mask="id")
        if results:
            return [result['id'] for result in results]
