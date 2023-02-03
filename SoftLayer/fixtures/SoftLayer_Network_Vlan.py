getObject = {
    'primaryRouter': {
        'datacenter': {'id': 1234, 'longName': 'TestDC'},
        'fullyQualifiedDomainName': 'fcr01.TestDC'
    },
    'id': 1234,
    'vlanNumber': 4444,
    'firewallInterfaces': None,
    'billingItem': {
        'allowCancellationFlag': 1,
        'categoryCode': 'network_vlan',
        'description': 'Private Network Vlan',
        'id': 235689,
        'notes': 'test cli',
        'orderItemId': 147258,
    },
    'subnets': [
        {
            'broadcastAddress': '169.46.22.127',
            'cidr': 28,
            'gateway': '169.46.22.113',
            'id': 1804813,
            'netmask': '255.255.255.240',
            'networkIdentifier': '169.46.22.112',
            'networkVlanId': 1404267,
            'subnetType': 'ADDITIONAL_PRIMARY',
            'totalIpAddresses': '16',
            'usableIpAddressCount': '13',
            'addressSpace': 'PUBLIC'
        },
        {
            'broadcastAddress': '150.239.7.191',
            'cidr': 27,
            'gateway': '150.239.7.161',
            'id': 2415982,
            'netmask': '255.255.255.224',
            'networkIdentifier': '150.239.7.160',
            'networkVlanId': 1404267,
            'subnetType': 'SECONDARY_ON_VLAN',
            'totalIpAddresses': '32',
            'usableIpAddressCount': '29',
            'version': 4,
            'addressSpace': 'PUBLIC'
        }],
    'hardware': [],
    'virtualGuests': [],
    'tagReferences': [],
}

editObject = True
setTags = True
getList = [getObject]

cancel = True

getCancelFailureReasons = [
    "1 bare metal server(s) still on the VLAN ",
    "1 virtual guest(s) still on the VLAN "
]
