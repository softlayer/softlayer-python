"""
    SoftLayer.network
    ~~~~~~~~~~~~~~~~~
    Network Manager/helpers

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""

from SoftLayer.utils import NestedDict, query_filter, IdentifierMixin, \
    resolve_ids


class NetworkManager(IdentifierMixin, object):
    """ Manage Networks """
    def __init__(self, client):
        #: A valid `SoftLayer.API.Client` object that will be used for all
        #: actions.
        self.client = client
        #: Reference to the SoftLayer_Account API object.
        self.account = client['Account']
        #: Reference to the SoftLayer_Network_Vlan object.
        self.vlan = client['Network_Vlan']
        self.subnet = client['Network_Subnet']
        self.subnet_resolvers = [self._get_subnet_by_identifier]

    def get_vlan(self, id):
        """ Returns information about a single VLAN.

        :param int id: The unique identifier for the VLAN
        :returns: A dictionary containing a large amount of information about
                  the specified VLAN.

        """
        return self.vlan.getObject(id=id, mask=self._get_vlan_mask())

    def get_subnet(self, id):
        """ Returns information about a single subnet.

        :param string id: Either the ID for the subnet or its network
                          identifier
        :returns: A dictionary of information about the subnet
        """
        id = resolve_ids(id, self.subnet_resolvers)[0]
        return self.subnet.getObject(id=id, mask='mask[%s]' %
                                     ','.join(self._get_subnet_mask()))

    def list_vlans(self, datacenter=None, vlan_number=None, **kwargs):
        """ Display a list of all VLANs on the account.

        This provides a quick overview of all VLANs including information about
        data center residence and the number of devices attached.

        :param string datacenter: If specified, the list will only contain
                                  VLANs in the specified data center.
        :param int vlan_number: If specified, the list will only contain the
                                VLAN matching this VLAN number.
        :param dict \*\*kwargs: response-level arguments (limit, offset, etc.)

        """
        _filter = NestedDict(kwargs.get('filter') or {})

        if vlan_number:
            _filter['networkVlans']['vlanNumber'] = query_filter(vlan_number)

        if datacenter:
            _filter['networkVlans']['primaryRouter']['datacenter']['name'] = \
                query_filter(datacenter)

        kwargs['filter'] = _filter.to_dict()

        return self._get_vlans(**kwargs)

    def list_subnets(self, identifier=None, datacenter=None, version=0,
                     **kwargs):
        """ Display a list of all subnets on the account.

        This provides a quick overview of all subnets including information
        about data center residence and the number of devices attached.

        :param string datacenter: If specified, the list will only contain
                                  subnets in the specified data center.
        :param dict \*\*kwargs: response-level arguments (limit, offset, etc.)

        """
        if 'mask' not in kwargs:
            mask = self._get_subnet_mask()
            kwargs['mask'] = 'mask[%s]' % ','.join(mask)

        _filter = NestedDict(kwargs.get('filter') or {})

        # TODO - I don't think filtering works on subnets in the API
        #if identifier:
        #    _filter['networkIdentifier'] = query_filter(identifier)
        #if datacenter:
        #    _filter['networkVlans']['primaryRouter']['datacenter']['name'] = \
        #        query_filter(datacenter)
        # if version:
        #     _filter['version'] = query_filter(version)

        kwargs['filter'] = _filter.to_dict()

        results = self.account.getSubnets(**kwargs)

        if any([version, identifier, datacenter]):
            if version:
                results = filter(lambda x: x['version'] == version, results)
            if identifier:
                results = filter(lambda x: x['networkIdentifier'] ==
                                 identifier, results)
            if datacenter:
                results = filter(lambda x: x['datacenter']['name'] ==
                                 datacenter, results)
        return results

    def summary_by_datacenter(self):
        """ Provides a dictionary with a summary of all network information on
        the account, grouped by data center.

        The resultant dictionary is primarily useful for statistical purposes.
        It contains count information rather than raw data. If you want raw
        information, see the :func:`list_vlans` method instead.

        :returns: A dictionary keyed by data center with the data containing a
                  series of counts for hardware, subnets, CCIs, and other
                  objects residing within that data center.

        """
        datacenters = {}
        for vlan in self._get_vlans():
            dc = vlan['primaryRouter']['datacenter']
            name = dc['name']
            if name not in datacenters:
                datacenters[name] = {
                    'hardwareCount': 0,
                    'networkingCount': 0,
                    'primaryIpCount': 0,
                    'subnetCount': 0,
                    'virtualGuestCount': 0,
                    'vlanCount': 0,
                }

            datacenters[name]['vlanCount'] += 1
            datacenters[name]['hardwareCount'] += len(vlan['hardware'])
            datacenters[name]['networkingCount'] += \
                len(vlan['networkComponents'])
            datacenters[name]['primaryIpCount'] += \
                vlan['totalPrimaryIpAddressCount']
            datacenters[name]['subnetCount'] += len(vlan['subnets'])
            datacenters[name]['virtualGuestCount'] += \
                len(vlan['virtualGuests'])

        return datacenters

    def _get_subnet_by_identifier(self, identifier):
        """ Returns the ID of the subnet matching the specified identifier.

        :param string identifier: The identifier to look up
        :returns: The ID of the matching subnet or None
        """
        results = self.list_subnets(identifier=identifier, mask='id')
        return [result['id'] for result in results]

    def _get_vlans(self, **kwargs):
        """ Returns a list of VLANs.

        Wrapper method for preventing duplicated code.

        :param dict \*\*kwargs: response-level arguments (limit, offset, etc.)

        """
        return self.account.getNetworkVlans(mask=self._get_vlan_mask(),
                                            **kwargs)

    @staticmethod
    def _get_subnet_mask():
        """ Returns the standard subnet object mask.

        Wrapper method to prevent duplicated code.

        """
        return [
            'hardware',
            'datacenter',
            'ipAddressCount',
            'virtualGuests',
        ]

    @staticmethod
    def _get_vlan_mask():
        """ Returns the standard VLAN object mask.

        Wrapper method for preventing duplicated code.

        """
        mask = [
            'firewallInterfaces',
            'hardware',
            'networkComponents',
            'primaryRouter[id, fullyQualifiedDomainName, datacenter]',
            'subnets',
            'totalPrimaryIpAddressCount',
            'virtualGuests',
        ]

        return 'mask[%s]' % ','.join(mask)
