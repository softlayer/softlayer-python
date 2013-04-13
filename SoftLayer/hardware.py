__all__ = ["HardwareManager"]


class HardwareManager(object):
    """ Manages hardware devices. """

    def __init__(self, client):
        """ HardwareManager initialization.

        :param SoftLayer.API.Client client: an API client instance

        """
        self.client = client
        self.hardware = self.client['Hardware_Server']
        self.account = self.client['Account']

    def list_hardware(self):
        """ List all hardware.

        """

        return self.account.getHardware()

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
                'notes',
                'privateNetworkOnlyFlag',
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
