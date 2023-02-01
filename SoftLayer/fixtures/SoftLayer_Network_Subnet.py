getObject = {
    'id': 1234,
    'billingItem': {
        'id': 1056
    },
    'number': 999,
    'networkIdentifier': '1.2.3.4',
    'cidr': '26',
    'subnetType': 'ADDITIONAL_PRIMARY',
    'networkVlan': {
        'networkSpace': 'PUBLIC',
        'primaryRouter': {
            'fullyQualifiedDomainName': 'fcr03a.dal13.softlayer.com'
        }
    },
    'gateway': '1.2.3.254',
    'broadcastAddress': '1.2.3.255',
    'datacenter': {
        'name': 'dal10',
        'id': 1
    },
    'virtualGuests': [
        {
            'hostname': 'hostname0',
            'domain': 'sl.test',
            'primaryIpAddress': '1.2.3.10',
            'primaryBackendIpAddress': '10.0.1.2'
        }
    ],
    'hardware': [],
    'usableIpAddressCount': 22,
    'note': 'test note',
    'tagReferences': [
        {'id': 1000123,
         'resourceTableId': 1234,
         'tag': {'id': 100123,
                 'name': 'subnet: test tag'},
         }
    ],
    'ipAddresses': [
        {'id': 123456,
         'ipAddress': '16.26.26.25'},
        {'id': 123457,
         'ipAddress': '16.26.26.26'}]
}

editNote = True
setTags = True
cancel = True
route = True
clearRoute = True
