"""
    SoftLayer.Network
    ~~~~~~~~~~~~~~~~~
    Network Manager/helpers

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""

from SoftLayer.utils import NestedDict, query_filter, IdentifierMixin


class NetworkManager(IdentifierMixin, object):
    """ Manage Networkss """
    def __init__(self, client):
        self.client = client
        self.account = client['Account']
        self.vlan = client['Network_Vlan']

    def get_vlan(self, id):
        return self.vlan.getObject(id=id, mask=self._get_vlan_mask())

    def list_vlans(self, datacenter=None, vlan_number=None, **kwargs):
        _filter = NestedDict(kwargs.get('filter') or {})

        if vlan_number:
            _filter['networkVlans']['vlanNumber'] = query_filter(vlan_number)

        if datacenter:
            _filter['networkVlans']['primaryRouter']['datacenter']['name'] = \
                query_filter(datacenter)

        kwargs['filter'] = _filter.to_dict()

        return self._get_vlans(**kwargs)

    def summary_by_datacenter(self):
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

    def _get_vlans(self, **kwargs):
        return self.account.getNetworkVlans(mask=self._get_vlan_mask(),
                                            **kwargs)

    @staticmethod
    def _get_vlan_mask():
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
