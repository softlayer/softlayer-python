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
        }
}

editObject = True
setTags = True
getList = [getObject]

cancel = True

getCancelFailureReasons = [
    "1 bare metal server(s) still on the VLAN ",
    "1 virtual guest(s) still on the VLAN "
]
