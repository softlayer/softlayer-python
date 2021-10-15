# https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_Listener/
updateLoadBalancerProtocols = {'accountId': 1234,
                               'address': '01-307608-ams01.clb.appdomain.cloud',
                               'createDate': '2019-08-12T07:49:43-06:00',
                               'id': 1111111,
                               'isPublic': 0,
                               'locationId': 265592,
                               'modifyDate': '2019-08-13T16:26:06-06:00',
                               'name': 'dcabero-01',
                               'operatingStatus': 'ONLINE',
                               'provisioningStatus': 'ACTIVE',
                               'type': 0,
                               'useSystemPublicIpPool': 1,
                               'uuid': '1a1aa111-4474-4e16-9f02-4de959229b85',
                               'listenerCount': 4,
                               'memberCount': 1,
                               'datacenter': {
                                   'id': 265592,
                                   'longName': 'Amsterdam 1',
                                   'name': 'ams01',
                                   'statusId': 2
                               }}
deleteLoadBalancerProtocols = {'accountId': 1234,
                               'address': '01-307608-ams01.clb.appdomain.cloud',
                               'createDate': '2019-08-12T07:49:43-06:00',
                               'id': 1111111,
                               'isPublic': 0,
                               'locationId': 265592,
                               'modifyDate': '2019-08-13T16:26:06-06:00',
                               'name': 'dcabero-01',
                               'operatingStatus': 'ONLINE',
                               'provisioningStatus': 'ACTIVE',
                               'type': 0,
                               'useSystemPublicIpPool': 1,
                               'uuid': '1a1aa111-4474-4e16-9f02-4de959229b85',
                               'listenerCount': 4,
                               'memberCount': 1,
                               'datacenter': {
                                   'id': 265592,
                                   'longName': 'Amsterdam 1',
                                   'name': 'ams01',
                                   'statusId': 2
                               }}

getL7Policies = [
    {'action': 'REJECT',
     'createDate': '2021-09-08T15:08:35-06:00',
     'id': 123456,
     'modifyDate': None,
     'name': 'test-reject',
     'priority': 2,
     'redirectL7PoolId': None,
     'uuid': '123mock-1234-43c9-b659-12345678mock'
     },
    {'action': 'REDIRECT_HTTPS',
     'createDate': '2021-09-08T15:03:53-06:00',
     'id': 432922,
     'modifyDate': None,
     'name': 'test-policy-https-1',
     'priority': 0,
     'redirectL7PoolId': None,
     'redirectUrl': 'url-test-uuid-mock-1234565',
     'uuid': 'test-uuid-mock-1234565'
     }
]
