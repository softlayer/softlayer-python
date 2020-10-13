IMAGES = [{
    'accountId': 1234,
    'blockDevices': [],
    'createDate': '2013-12-05T21:53:03-06:00',
    'globalIdentifier': '0B5DEAF4-643D-46CA-A695-CECBE8832C9D',
    'id': 100,
    'name': 'test_image',
    'parentId': '',
    'publicFlag': True,
    'children': [{
        'datacenter': {
            'name': 'ams01'
        }
    }],
}, {
    'accountId': 1234,
    'blockDevices': [],
    'createDate': '2013-12-05T21:53:03-06:00',
    'globalIdentifier': 'EB38414C-2AB3-47F3-BBBD-56A5F689620B',
    'id': 101,
    'name': 'test_image2',
    'parentId': '',
    'publicFlag': True,
    'children': [{
        'datacenter': {
            'name': 'ams01'
        }
    }],
}]

getObject = IMAGES[0]
getPublicImages = IMAGES
deleteObject = {}
editObject = True
setTags = True
createFromExternalSource = {
    'createDate': '2013-12-05T21:53:03-06:00',
    'globalIdentifier': '0B5DEAF4-643D-46CA-A695-CECBE8832C9D',
    'id': 100,
    'name': 'test_image',
}
createFromIcos = {
    'createDate': '2013-12-05T21:53:03-06:00',
    'globalIdentifier': '0B5DEAF4-643D-46CA-A695-CECBE8832C9D',
    'id': 100,
    'name': 'test_image',
}
copyToExternalSource = True
copyToIcos = True
addLocations = True
removeLocations = True
getStorageLocations = [
    {'id': 265592, 'longName': 'Amsterdam 1', 'name': 'ams01', 'statusId': 2},
    {'id': 814994, 'longName': 'Amsterdam 3', 'name': 'ams03', 'statusId': 2},
]
