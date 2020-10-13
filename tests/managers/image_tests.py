"""
    SoftLayer.tests.managers.image_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import SoftLayer
from SoftLayer import exceptions
from SoftLayer import testing

IMAGE_SERVICE = 'SoftLayer_Virtual_Guest_Block_Device_Template_Group'


class ImageTests(testing.TestCase):

    def set_up(self):
        self.image = SoftLayer.ImageManager(self.client)
        self.vgbdtg = self.client['']
        self.account = self.client['Account']

    def test_get_image(self):
        result = self.image.get_image(100)

        self.assertEqual(result['id'], 100)
        self.assertEqual(result['name'], 'test_image')
        self.assertEqual(result['accountId'], 1234)
        self.assert_called_with(IMAGE_SERVICE, 'getObject', identifier=100)

    def test_delete_image(self):
        self.image.delete_image(100)

        self.assert_called_with(IMAGE_SERVICE, 'deleteObject', identifier=100)

    def test_list_private_images(self):
        results = self.image.list_private_images()

        self.assertEqual(len(results), 2)
        self.assert_called_with('SoftLayer_Account',
                                'getPrivateBlockDeviceTemplateGroups')

    def test_list_private_images_with_filters(self):
        results = self.image.list_private_images(
            guid='0FA9ECBD-CF7E-4A1F-1E36F8D27C2B', name='name')

        self.assertEqual(len(results), 2)
        _filter = {
            'privateBlockDeviceTemplateGroups': {
                'globalIdentifier': {
                    'operation': '_= 0FA9ECBD-CF7E-4A1F-1E36F8D27C2B'},
                'name': {'operation': '_= name'}}
        }
        self.assert_called_with('SoftLayer_Account',
                                'getPrivateBlockDeviceTemplateGroups',
                                filter=_filter)

    def test_list_public_images(self):
        results = self.image.list_public_images()

        self.assertEqual(len(results), 2)
        self.assert_called_with(IMAGE_SERVICE, 'getPublicImages')

    def test_list_public_images_with_filters(self):
        results = self.image.list_public_images(
            guid='0FA9ECBD-CF7E-4A1F-1E36F8D27C2B', name='name')

        _filter = {
            'globalIdentifier': {
                'operation': '_= 0FA9ECBD-CF7E-4A1F-1E36F8D27C2B'},
            'name': {'operation': '_= name'}
        }
        self.assertEqual(len(results), 2)
        self.assert_called_with(IMAGE_SERVICE, 'getPublicImages',
                                filter=_filter)

    def test_resolve_ids_guid(self):
        result = self.image.resolve_ids('3C1F3C68-0B67-4F5E-8907-D0FC84BF3F12')

        self.assertEqual(['3C1F3C68-0B67-4F5E-8907-D0FC84BF3F12'], result)

    def test_resolve_ids_name_public(self):
        public_mock = self.set_mock(IMAGE_SERVICE, 'getPublicImages')
        public_mock.return_value = [{'id': 100}]
        private_mock = self.set_mock('SoftLayer_Account',
                                     'getPrivateBlockDeviceTemplateGroups')
        private_mock.return_value = []

        self.account.getPrivateBlockDeviceTemplateGroups.return_value = []

        result = self.image.resolve_ids('image_name')
        self.assertEqual([100], result)

    def test_resolve_ids_name_private(self):
        public_mock = self.set_mock(IMAGE_SERVICE, 'getPublicImages')
        public_mock.return_value = []
        private_mock = self.set_mock('SoftLayer_Account',
                                     'getPrivateBlockDeviceTemplateGroups')
        private_mock.return_value = [{'id': 100}]

        result = self.image.resolve_ids('private_image_name')
        self.assertEqual([100], result)

    def test_resolve_ids_not_found(self):
        public_mock = self.set_mock(IMAGE_SERVICE, 'getPublicImages')
        public_mock.return_value = []
        private_mock = self.set_mock('SoftLayer_Account',
                                     'getPrivateBlockDeviceTemplateGroups')
        private_mock.return_value = []

        result = self.image.resolve_ids('unknown_name')
        self.assertEqual([], result)

    def test_edit_tags(self):
        # Test updating tags
        self.image.edit(1, tag="tag1,tag2")

        self.assert_called_with(IMAGE_SERVICE, 'setTags',
                                identifier=1,
                                args=("tag1,tag2",))

    def test_edit_blank(self):
        # Test a blank edit
        result = self.image.edit(1)

        self.assertEqual(result, False)
        self.assertEqual(self.calls(IMAGE_SERVICE, 'setTags'), [])

    def test_edit_full(self):
        # Finally test a full edit
        self.image.edit(1, name='abc', note='xyz')
        self.assert_called_with(IMAGE_SERVICE, 'editObject',
                                identifier=1,
                                args=({'name': 'abc', 'note': 'xyz'},))

    def test_import_image(self):
        self.image.import_image_from_uri(name='test_image',
                                         note='testimage',
                                         uri='someuri',
                                         os_code='UBUNTU_LATEST')

        self.assert_called_with(
            IMAGE_SERVICE,
            'createFromExternalSource',
            args=({'name': 'test_image',
                   'note': 'testimage',
                   'uri': 'someuri',
                   'operatingSystemReferenceCode': 'UBUNTU_LATEST'},))

    def test_import_image_cos(self):
        self.image.import_image_from_uri(name='test_image',
                                         note='testimage',
                                         uri='cos://some_uri',
                                         os_code='UBUNTU_LATEST',
                                         ibm_api_key='some_ibm_key',
                                         root_key_crn='some_root_key_crn',
                                         wrapped_dek='some_dek',
                                         cloud_init=False,
                                         byol=False,
                                         is_encrypted=False
                                         )

        self.assert_called_with(
            IMAGE_SERVICE,
            'createFromIcos',
            args=({'name': 'test_image',
                   'note': 'testimage',
                   'operatingSystemReferenceCode': 'UBUNTU_LATEST',
                   'uri': 'cos://some_uri',
                   'ibmApiKey': 'some_ibm_key',
                   'crkCrn': 'some_root_key_crn',
                   'wrappedDek': 'some_dek',
                   'cloudInit': False,
                   'byol': False,
                   'isEncrypted': False
                   },))

    def test_export_image(self):
        self.image.export_image_to_uri(1234, 'someuri')

        self.assert_called_with(
            IMAGE_SERVICE,
            'copyToExternalSource',
            args=({'uri': 'someuri'},),
            identifier=1234)

    def test_export_image_cos(self):
        self.image.export_image_to_uri(1234,
                                       'cos://someuri',
                                       ibm_api_key='someApiKey')

        self.assert_called_with(
            IMAGE_SERVICE,
            'copyToIcos',
            args=({'uri': 'cos://someuri', 'ibmApiKey': 'someApiKey'},),
            identifier=1234)

    def test_add_locations_image(self):
        locations = ['ams01']
        self.image.add_locations(100, locations)

        self.assert_called_with(IMAGE_SERVICE, 'addLocations', identifier=100)

    def test_add_locations_fail(self):
        locations = ['test']
        self.assertRaises(
            exceptions.SoftLayerError,
            self.image.add_locations,
            100,
            locations
        )

    def test_remove_locations_image(self):
        locations = ['ams01']
        self.image.remove_locations(100, locations)

        self.assert_called_with(IMAGE_SERVICE, 'removeLocations', identifier=100)

    def test_get_locations_id_fails(self):
        locations = ['test']
        self.assertRaises(
            exceptions.SoftLayerError,
            self.image.get_locations_list,
            100,
            locations
        )
