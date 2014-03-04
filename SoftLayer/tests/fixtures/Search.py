
search = [{
    'resourceType': 'SoftLayer_Virtual_Guest',
    'relevanceScore': '2.3468237',
    'resource': {
        'id': 123,
        'fullyQualifiedDomainName': 'app1.example.com'
    },
    'matchedTerms': ['app1', 'app1.example.com']
}, {
    'resourceType': 'SoftLayer_Network_Subnet_IpAddress',
    'relevanceScore': '0.04867386',
    'resource': {
        'ipAddress': '173.192.125.114',
        'id': 234
    },
    'matchedTerms': ['app1.example.com']
}, {
    'resourceType': 'SoftLayer_Ticket',
    'relevanceScore': '0.04435336',
    'resource': {
        'id': 345,
        'title': 'MONITORING: Network Monitor Alert A REALLY LONG TITLE FOR ME ------------'
    },
    'matchedTerms': ['app1.example.com']
}]

getObjectTypes = [{
    'name': 'SoftLayer_Network_Vlan',
    'properties': [
        {'type': 'integer', 'name': 'accountId', 'sortableFlag': False},
        {'type': 'string', 'name': 'name', 'sortableFlag': True},
        {'type': 'text', 'name': 'note', 'sortableFlag': False},
        {'type': 'string', 'name': 'primaryRouter.datacenter.longName', 'sortableFlag': True},
        {'type': 'string', 'name': 'primaryRouter.hostname', 'sortableFlag': True},
        {'type': 'string', 'name': 'tagReferences.tag.name', 'sortableFlag': True},
        {'type': 'string', 'name': 'vlanNumber', 'sortableFlag': True}
    ]
}, {
    'name': 'SoftLayer_Network_Vlan_Firewall',
    'properties': [
        {'type': 'string', 'name': 'datacenter.longName', 'sortableFlag': True},
        {'type': 'string', 'name': 'fullyQualifiedDomainName', 'sortableFlag': True},
        {'type': 'integer', 'name': 'networkVlan.accountId', 'sortableFlag': False},
        {'type': 'string', 'name': 'networkVlans.id', 'sortableFlag': True},
        {'type': 'string', 'name': 'primaryIpAddress', 'sortableFlag': True},
        {'type': 'string', 'name': 'tagReferences.tag.name', 'sortableFlag': True}
    ]
}, {
    'name': 'SoftLayer_Event_Log',
    'properties': [
        {'type': 'string', 'name': 'datacenter.longName', 'sortableFlag': True},
        {'type': 'string', 'name': 'fullyQualifiedDomainName', 'sortableFlag': True},
        {'type': 'integer', 'name': 'networkVlan.accountId', 'sortableFlag': False},
        {'type': 'string', 'name': 'networkVlans.id', 'sortableFlag': True},
        {'type': 'string', 'name': 'primaryIpAddress', 'sortableFlag': True},
        {'type': 'string', 'name': 'tagReferences.tag.name', 'sortableFlag': True}
    ]
}]
