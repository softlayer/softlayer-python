"""
    SoftLayer.tests.mocks.image_mock
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
from mock import MagicMock

IMAGES = [{
    'accountId': 1234,
    'blockDevices': [],
    'createDate': '2013-12-05T21:53:03-06:00',
    'globalIdentifier': '0B5DEAF4-643D-46CA-A695-CECBE8832C9D',
    'id': 100,
    'name': 'test_image',
    'parentId': ''
}, {
    'accountId': 1234,
    'blockDevices': [],
    'createDate': '2013-12-05T21:53:03-06:00',
    'globalIdentifier': 'EB38414C-2AB3-47F3-BBBD-56A5F689620B',
    'id': 101,
    'name': 'test_image2',
    'parentId': ''
}]

IMAGE_MAP = {
    100: IMAGES[0],
    101: IMAGES[1]
}


def getObject_Mock(image_id):
    mock = MagicMock()
    mock.return_value = IMAGE_MAP[image_id]
    return mock


def image_list_mock():
    mock = MagicMock()
    mock.return_value = IMAGES
    return mock
