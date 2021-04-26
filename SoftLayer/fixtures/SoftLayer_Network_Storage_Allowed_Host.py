TEST_ALLOWED_HOST = {
    'id': 12345,
    'name': 'Test Allowed Host',
    'accountId': 1234,
    'credentialId': None,
    'createDate': '2020-01-01 00:00:01',
    'iscsiAclCredentials': {
        'id': 129,
        'allowedHostId': 12345,
        'subnetId': 12345678
    },
    'subnetsInAcl': [{
        'id': 12345678,
        'accountId': 1234,
        'networkIdentifier': '10.11.12.13',
        'cidr': '14',
        'billingRecordId': None,
        'parentId': None,
        'networkVlanId': None,
        'createDate': '2020-01-02 00:00:01',
        'modifyDate': None,
        'subnetType': 'SECONDARY_ON_VLAN',
        'restrictAllocationFlag': 0,
        'leafFlag': 1,
        'ownerId': 1,
        'ipAddressBegin': 129123,
        'ipAddressEnd': 129145,
        'purgeFlag': 0
    }]
}

getObject = TEST_ALLOWED_HOST

getSubnetsInAcl = [{
    'id': 12345678,
    'accountId': 1234,
    'networkIdentifier': '10.11.12.13',
    'cidr': '14',
    'billingRecordId': None,
    'parentId': None,
    'networkVlanId': None,
    'createDate': '2020-01-02 00:00:01',
    'modifyDate': None,
    'subnetType': 'SECONDARY_ON_VLAN',
    'restrictAllocationFlag': 0,
    'leafFlag': 1,
    'ownerId': 1,
    'ipAddressBegin': 129123,
    'ipAddressEnd': 129145,
    'purgeFlag': 0
}]

assignSubnetsToAcl = [
    12345678
]

removeSubnetsFromAcl = [
    12345678
]

setCredentialPassword = True
