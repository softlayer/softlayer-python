IMAGES = [{
    'accountId': 1234,
    'blockDevices': [],
    'createDate': '2013-12-05T21:53:03-06:00',
    'globalIdentifier': '0B5DEAF4-643D-46CA-A695-CECBE8832C9D',
    'id': 100,
    'name': 'test_image',
    'parentId': '',
    'note': 'image_note',
    'tagReferences': [{'tag': {'name': 'Image_Tags'}}],
    'status': {'name': 'Active'},
    'children': [{'blockDevices': [{'diskImage': {'capacity': 25,
                                    'units': 'GB', 'type': {'name': 'System'}},
                                    'diskSpace': 1232423421234, 'units': 'B'},
                                    {'diskImage': {'type': {'name': 'Swap'}}}]}
]}, {
    'accountId': 1234,
    'blockDevices': [],
    'createDate': '2013-12-05T21:53:03-06:00',
    'globalIdentifier': 'EB38414C-2AB3-47F3-BBBD-56A5F689620B',
    'id': 101,
    'name': 'test_image2',
    'parentId': ''
}]

getObject = IMAGES[0]
getPublicImages = IMAGES
deleteObject = {}
