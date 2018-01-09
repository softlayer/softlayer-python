getAllObjects = [
    {'id': 100,
     'name': 'secgroup1',
     'description': 'Securitygroup1'},
    {'id': 104,
     'name': 'secgroup2'},
    {'id': 110}
]

getRules = [
    {'id': 100,
     'direction': 'egress',
     'ethertype': 'IPv4'}
]

guest_dict = {'id': 5000,
              'hostname': 'test',
              'primaryBackendIpAddress': '10.3.4.5',
              'primaryIpAddress': '169.23.123.43'}

getObject = {
    'id': 100,
    'name': 'secgroup1',
    'description': 'Securitygroup1',
    'networkComponentBindings': [{'networkComponentId': 1000,
                                  'networkComponent': {'id': 1000,
                                                       'port': 0,
                                                       'guest': guest_dict}},
                                 {'networkComponentId': 1001,
                                  'networkComponent': {'id': 1001,
                                                       'port': 1,
                                                       'guest': guest_dict}}],
    'rules': getRules
}

createObject = {'id': 100,
                'name': 'secgroup1',
                'description': 'Securitygroup1',
                'createDate': '2017-05-05T12:44:43-06:00'}
editObject = True
deleteObject = True
addRules = {"requestId": "addRules",
            "rules": "[{'direction': 'ingress', "
                     "'portRangeMax': '', "
                     "'portRangeMin': '', "
                     "'ethertype': 'IPv4', "
                     "'securityGroupId': 100, "
                     "'remoteGroupId': '', "
                     "'id': 100}]"}
editRules = {'requestId': 'editRules'}
removeRules = {'requestId': 'removeRules'}
attachNetworkComponents = {'requestId': 'interfaceAdd'}
detachNetworkComponents = {'requestId': 'interfaceRemove'}
