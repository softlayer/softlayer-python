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

getObject_no_hard_no_vs_no_trunk = {'primaryRouter': {'fullyQualifiedDomainName': 'bcr02a.fra02.softlayer.com',
                                                      'id': 1186647,
                                                      'datacenter': {'id': 449506,
                                                                     'longName': 'Frankfurt 2',
                                                                     'name': 'fra02'}
                                                      },
                                    'id': 1186647,
                                    'vlanNumber': 932,
                                    'networkVlanFirewall': {
                                        'datacenter': {'id': 449506, 'longName': 'Frankfurt 2'},
                                        'fullyQualifiedDomainName': 'bcr02a.fra02.softlayer.com'
                                        },
                                    'subnets': [
                                        {'gateway': '10.85.154.1',
                                         'id': 1688651,
                                         'netmask': '255.255.255.192',
                                         'networkIdentifier': '10.85.154.0',
                                         'subnetType': 'ADDITIONAL_PRIMARY',
                                         'usableIpAddressCount': '61'}],
                                    'hardware': [
                                        {'domain': 'vmware.chechu.com',
                                         'hostname': 'host15',
                                         'primaryBackendIpAddress': '10.177.122.170',
                                         'primaryIpAddress': '169.46.48.107'}],
                                    'virtualGuests': [
                                        {'domain': 'ocp-virt.chechu.me',
                                         'hostname': 'haproxy',
                                         'primaryBackendIpAddress': '10.85.154.44',
                                         'primaryIpAddress': '158.177.72.67'}],
                                    'networkComponentTrunks': [
                                        {'networkComponent':
                                            {'hardwareId': 1483895, 'networkVlanId': 3285524, 'port': 12,
                                             'downlinkComponent': {'networkVlanId': '', 'port': 0,
                                                                   'primaryIpAddress': '10.194.250.148',
                                                                   'hardware':
                                                                       {
                                                                           'domain': 'chechu.me',
                                                                           'hostname': 'fra02-ocp-virt',
                                                                           'tagReferences': []
                                                                           },
                                                                       'networkComponentGroup': {
                                                                           'groupTypeId': 1,
                                                                           'membersDescription': 'eth0/2'}}}}],
                                    'tagReferences': []}

editObject = True
setTags = True
getList = [getObject]

cancel = True

getCancelFailureReasons = [
    "1 bare metal server(s) still on the VLAN ",
    "1 virtual guest(s) still on the VLAN "
]
