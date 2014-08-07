"""
    SoftLayer.tests.managers.image_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

import SoftLayer
from SoftLayer import testing
from SoftLayer.testing import fixtures


class ImageTests(testing.TestCase):

    def set_up(self):
        self.client = testing.FixtureClient()
        self.image = SoftLayer.ImageManager(self.client)
        self.vgbdtg = self.client['Virtual_Guest_Block_Device_Template_Group']
        self.account = self.client['Account']

    def test_get_image(self):
        result = self.image.get_image(100)

        self.vgbdtg.getObject.assert_called_once_with(id=100, mask=mock.ANY)
        self.assertEqual(
            result,
            fixtures.Virtual_Guest_Block_Device_Template_Group.getObject)

    def test_delete_image(self):
        self.image.delete_image(100)

        self.vgbdtg.deleteObject.assert_called_once_with(id=100)

    def test_list_private_images(self):
        results = self.image.list_private_images()

        f = self.account.getPrivateBlockDeviceTemplateGroups
        f.assert_called_once_with(filter={}, mask=mock.ANY)
        self.assertEqual(results,
                         fixtures.Account.getPrivateBlockDeviceTemplateGroups)

    def test_list_private_images_with_filters(self):
        results = self.image.list_private_images(
            guid='0FA9ECBD-CF7E-4A1F-1E36F8D27C2B', name='name')

        f = self.account.getPrivateBlockDeviceTemplateGroups
        f.assert_called_once_with(
            filter={
                'privateBlockDeviceTemplateGroups': {
                    'globalIdentifier': {
                        'operation': '_= 0FA9ECBD-CF7E-4A1F-1E36F8D27C2B'},
                    'name': {'operation': '_= name'}}},
            mask=mock.ANY)
        self.assertEqual(results,
                         fixtures.Account.getPrivateBlockDeviceTemplateGroups)

    def test_list_public_images(self):
        results = self.image.list_public_images()

        self.vgbdtg.getPublicImages.assert_called_once_with(filter={},
                                                            mask=mock.ANY)
        self.assertEqual(
            results,
            fixtures.Virtual_Guest_Block_Device_Template_Group.getPublicImages)

    def test_list_public_images_with_filters(self):
        results = self.image.list_public_images(
            guid='0FA9ECBD-CF7E-4A1F-1E36F8D27C2B', name='name')

        self.vgbdtg.getPublicImages.assert_called_once_with(
            filter={
                'globalIdentifier': {
                    'operation': '_= 0FA9ECBD-CF7E-4A1F-1E36F8D27C2B'},
                'name': {'operation': '_= name'}},
            mask=mock.ANY)
        self.assertEqual(
            results,
            fixtures.Virtual_Guest_Block_Device_Template_Group.getPublicImages)

    def test_resolve_ids_guid(self):
        result = self.image.resolve_ids('3C1F3C68-0B67-4F5E-8907-D0FC84BF3F12')

        self.assertEqual(['3C1F3C68-0B67-4F5E-8907-D0FC84BF3F12'], result)

    def test_resolve_ids_name_public(self):
        self.vgbdtg.getPublicImages.return_value = [{'id': 100}]
        self.account.getPrivateBlockDeviceTemplateGroups.return_value = []
        result = self.image.resolve_ids('image_name')

        self.assertEqual([100], result)

    def test_resolve_ids_name_private(self):
        self.vgbdtg.getPublicImages.return_value = []
        self.account.getPrivateBlockDeviceTemplateGroups.return_value = (
            [{'id': 100}])
        result = self.image.resolve_ids('private_image_name')

        self.assertEqual([100], result)

    def test_resolve_ids_not_found(self):
        self.vgbdtg.getPublicImages.return_value = []
        self.account.getPrivateBlockDeviceTemplateGroups.return_value = []
        result = self.image.resolve_ids('unknown_name')

        self.assertEqual([], result)

    def test_edit(self):
        # Test updating tags
        self.image.edit(1, tag="tag1,tag2")
        self.vgbdtg.setTags.assert_called_once_with("tag1,tag2", id=1)

        # Test a blank edit
        self.image.edit(1)
        self.assertTrue(self.image.edit, 1)

        # Finally test a full edit
        args = {
            'name': 'abc',
            'note': 'xyz'
        }
        self.image.edit(1, **args)
        self.vgbdtg.editObject.assert_called_once_with(args, id=1)
