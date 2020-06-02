"""
    SoftLayer.tests.managers.tag_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.exceptions import SoftLayerAPIError
from SoftLayer.managers import tags
from SoftLayer import testing


class TagTests(testing.TestCase):

    def set_up(self):
        self.tag_manager = tags.TagManager(self.client)
        self.test_mask = "mask[id]"

    def test_list_tags(self):
        result = self.tag_manager.list_tags()
        self.assert_called_with('SoftLayer_Tag', 'getUnattachedTagsForCurrentUser')
        self.assert_called_with('SoftLayer_Tag', 'getAttachedTagsForCurrentUser')
        self.assertIn('attached', result.keys())
        self.assertIn('unattached', result.keys())

    def test_list_tags_mask(self):
        result = self.tag_manager.list_tags(mask=self.test_mask)
        self.assert_called_with('SoftLayer_Tag', 'getUnattachedTagsForCurrentUser', mask=self.test_mask)
        self.assert_called_with('SoftLayer_Tag', 'getAttachedTagsForCurrentUser', mask=self.test_mask)
        self.assertIn('attached', result.keys())
        self.assertIn('unattached', result.keys())

    def test_unattached_tags(self):
        result = self.tag_manager.get_unattached_tags()
        self.assertEqual('coreos', result[0].get('name'))
        self.assert_called_with('SoftLayer_Tag', 'getUnattachedTagsForCurrentUser', mask=None)

    def test_unattached_tags_mask(self):
        result = self.tag_manager.get_unattached_tags(mask=self.test_mask)
        self.assertEqual('coreos', result[0].get('name'))
        self.assert_called_with('SoftLayer_Tag', 'getUnattachedTagsForCurrentUser', mask=self.test_mask)

    def test_attached_tags(self):
        result = self.tag_manager.get_attached_tags()
        self.assertEqual('bs_test_instance', result[0].get('name'))
        self.assert_called_with('SoftLayer_Tag', 'getAttachedTagsForCurrentUser', mask=None)

    def test_attached_tags_mask(self):
        result = self.tag_manager.get_attached_tags(mask=self.test_mask)
        self.assertEqual('bs_test_instance', result[0].get('name'))
        self.assert_called_with('SoftLayer_Tag', 'getAttachedTagsForCurrentUser', mask=self.test_mask)

    def test_get_tag_references(self):
        tag_id = 1286571
        result = self.tag_manager.get_tag_references(tag_id)
        self.assertEqual(tag_id, result[0].get('tagId'))
        self.assert_called_with('SoftLayer_Tag', 'getReferences', identifier=tag_id)

    def test_get_tag_references_mask(self):
        tag_id = 1286571
        result = self.tag_manager.get_tag_references(tag_id, mask=self.test_mask)
        self.assertEqual(tag_id, result[0].get('tagId'))
        self.assert_called_with('SoftLayer_Tag', 'getReferences', identifier=tag_id, mask=self.test_mask)

    def test_reference_lookup_hardware(self):
        resource_id = 12345
        tag_type = 'HARDWARE'

        self.tag_manager.reference_lookup(resource_id, tag_type)
        self.assert_called_with('SoftLayer_Hardware', 'getObject', identifier=resource_id)

    def test_reference_lookup_guest(self):
        resource_id = 12345
        tag_type = 'GUEST'

        self.tag_manager.reference_lookup(resource_id, tag_type)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'getObject', identifier=resource_id)

    def test_reference_lookup_app_delivery(self):
        resource_id = 12345
        tag_type = 'APPLICATION_DELIVERY_CONTROLLER'

        self.tag_manager.reference_lookup(resource_id, tag_type)
        self.assert_called_with('SoftLayer_Network_Application_Delivery_Controller',
                                'getObject', identifier=resource_id)

    def test_reference_lookup_dedicated(self):
        resource_id = 12345
        tag_type = 'DEDICATED_HOST'

        self.tag_manager.reference_lookup(resource_id, tag_type)
        self.assert_called_with('SoftLayer_Virtual_DedicatedHost', 'getObject', identifier=resource_id)

    def test_reference_lookup_document(self):
        resource_id = 12345
        tag_type = 'ACCOUNT_DOCUMENT'

        exception = self.assertRaises(
            SoftLayerAPIError,
            self.tag_manager.reference_lookup,
            resource_id,
            tag_type
        )
        self.assertEqual(exception.faultCode, 404)
        self.assertEqual(exception.reason, "Unable to lookup ACCOUNT_DOCUMENT types")
