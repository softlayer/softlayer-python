"""
    SoftLayer.tests.managers.image_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import ImageManager
from SoftLayer.tests import unittest
from SoftLayer.tests.mocks import image_mock

from mock import MagicMock, ANY


class ImageTests(unittest.TestCase):

    def setUp(self):
        self.client = MagicMock()
        self.image = ImageManager(self.client)
        self.vgbdtg = self.client['Virtual_Guest_Block_Device_Template_Group']

    def test_get_image(self):
        self.vgbdtg.getObject = image_mock.getObject_Mock(100)
        result = self.image.get_image(100)

        self.vgbdtg.getObject.assert_called_once_with(id=100, mask=ANY)
        expected = image_mock.IMAGE_MAP[100]
        self.assertEqual(expected, result)

    def test_delete_image(self):
        self.image.delete_image(100)

        self.vgbdtg.deleteObject.assert_called_once_with(id=100)

    def test_list_private_images(self):
        f = self.client['Account'].getPrivateBlockDeviceTemplateGroups = \
            image_mock.image_list_mock()
        results = self.image.list_private_images()

        f.assert_called_once_with(filter={}, mask=ANY)
        self.assertEqual(results, image_mock.IMAGES)

    def test_list_public_images(self):
        f = self.vgbdtg.getPublicImages = image_mock.image_list_mock()
        results = self.image.list_public_images()

        f.assert_called_once_with(filter={}, mask=ANY)
        self.assertEqual(results, image_mock.IMAGES)
