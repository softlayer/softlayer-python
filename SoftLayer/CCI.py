"""
    SoftLayer.CCI
    ~~~~~~~~~~~~~
    CCI Manager/helpers

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from SoftLayer.exceptions import SoftLayerError


class CCICreateMissingRequired(SoftLayerError):
    def __init__(self):
        self.message = "cpu, memory, hostname, and domain are required"


class CCICreateMutuallyExclusive(SoftLayerError):
    def __init__(self, *args):
        self.message = "Can only specify one of:", ','.join(args)


class CCIManager(object):
    """ Manage CCIs """
    def __init__(self, client):
        self.client = client
        self.account = client['Account']
        self.guest = client['Virtual_Guest']

    def list_instances(self, hourly=True, monthly=True, tags=None, **kwargs):
        """ Retrieve a list of all CCIs on the account.

        :param boolean hourly: include hourly instances
        :param boolean monthly: include monthly instances
        :param list tags: filter based on tags
        :param dict **kwargs: response-level arguments (limit, offset, etc.)

        """
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

        call = 'getVirtualGuests'
        if not all([hourly, monthly]):
            if hourly:
                call = 'getHourlyVirtualGuests'
            elif monthly:
                call = 'getMonthlyVirtualGuests'

        mask = "mask[%s]" % ','.join(items)

        _filter = None
        if tags:
            _filter = {
                'virtualGuests': {
                    'tagReferences': {
                        'tag': {'name': {
                            'operation': 'in',
                            'options': {'name': 'data', 'value': tags}
                        }}
                    }
                }
            }

        func = getattr(self.account, call)
        return func(mask=mask, filter=_filter)

    def get_instance(self, id):
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

        mask = "mask[%s]" % ','.join(items)

        return self.guest.getObject(mask=mask, id=id)

    def get_instance_passwords(self, id):
        """ Returns a list of passwords for an instance. """
        os_info = self.guest.getOperatingSystem(mask='mask.passwords', id=id)
        return os_info['passwords'] if 'passwords' in os_info else []

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
                'primaryNetworkComponent':
                    {"networkVlan": {"id": int(public_vlan)}}})
        if private_vlan:
            data.update({
                "primaryBackendNetworkComponent":
                    {"networkVlan": {"id": int(private_vlan)}}})

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
