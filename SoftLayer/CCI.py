from SoftLayer.exceptions import SoftLayerError


class CCICreateMissingRequired(SoftLayerError):
    def __init__(self):
        self.message = "cpu, memory, hostname, and domain are required"


class CCICreateMutuallyExclusive(SoftLayerError):
    def __init__(self, *args):
        self.message = "Can only specify one of:", ','.join(args)


class CCIManager(object):
    """ Manage CCI's """
    def __init__(self, client):
        self.client = client
        self.account = client['Account']
        self.guest = client['Virtual_Guest']

    def list_instances(self, hourly=True, monthly=True):
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
        ])

        call = 'getVirtualGuests'
        if not all([hourly, monthly]):
            if hourly:
                call = 'getHourlyVirtualGuests'
            elif monthly:
                call = 'getMonthlyVirtualGuests'

        mask = "mask[%s]" % ','.join(items)

        func = getattr(self.account, call)
        return func(mask=mask)

    def get_instance(self, id):
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
            'activeTransaction.id',
            'blockDeviceTemplateGroup[id, name]',
            'status.name',
            'operatingSystem.softwareLicense.'
            'softwareDescription[manufacturer,name, version]',
            'operatingSystem.passwords[username,password]',
            'billingItem.recurringFee',
        ])

        mask = "mask[{0}]".format(','.join(items))

        return self.guest.getObject(mask=mask, id=id)

    def get_create_options(self):
        return self.guest.getCreateObjectOptions()

    def cancel_instance(self, id):
        return self.guest.deleteObject(id=id)

    def _generate_create_dict(
            self, cpus=None, memory=None, hourly=True,
            hostname=None, domain=None, local_disk=True,
            datacenter=None, os_code=None, image_id=None,
            private=False, public_vlan=None, private_vlan=None):

        required = [cpus, memory, hostname, domain]

        mutually_exclusive = [
            {'os_code': os_code, "image_id": image_id},
        ]

        if not all(required):
            raise CCICreateMissingRequired()

        for me in mutually_exclusive:
            if all(me.values()):
                raise CCICreateMutuallyExclusive(*me.key())

        data = {
            "startCpus": int(cpus),
            "maxMemory": int(memory),
            "hostname": hostname,
            "domain": domain,
            "localDiskFlag": local_disk,
        }

        if hourly:
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
            data["primaryNetworkCompnent"]["networkVlan"]["id"] = \
                int(public_vlan)

        if private_vlan:
            data["primaryBackendNetworkCompnent"]["networkVlan"]["id"] = \
                int(private_vlan)

        return data

    def verify_create_instance(self, **kwargs):
        """ see _generate_create_dict """
        create_options = self._generate_create_dict(**kwargs)
        return self.guest.generateOrderTemplate(create_options)

    def create_instance(self, **kwargs):
        """ see _generate_create_dict """
        create_options = self._generate_create_dict(**kwargs)
        return self.guest.createObject(create_options)
