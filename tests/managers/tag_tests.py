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

    def test_set_tags(self):
        tags = "tag1,tag2"
        key_name = "GUEST"
        resource_id = 100

        self.tag_manager.set_tags(tags, key_name, resource_id)
        self.assert_called_with('SoftLayer_Tag', 'setTags')

    def test_get_tag(self):
        tag_id = 1286571
        result = self.tag_manager.get_tag(tag_id)
        self.assertEqual(tag_id, result.get('id'))
        self.assert_called_with('SoftLayer_Tag', 'getObject', identifier=tag_id)

    def test_get_tag_mask(self):
        tag_id = 1286571
        result = self.tag_manager.get_tag(tag_id, mask=self.test_mask)
        self.assertEqual(tag_id, result.get('id'))
        self.assert_called_with('SoftLayer_Tag', 'getObject', identifier=tag_id, mask=self.test_mask)

    def test_get_tag_by_name(self):
        tag_name = 'bs_test_instance'
        result = self.tag_manager.get_tag_by_name(tag_name)
        args = (tag_name,)
        self.assertEqual(tag_name, result[0].get('name'))
        self.assert_called_with('SoftLayer_Tag', 'getTagByTagName', args=args)

    def test_get_tag_by_name_mask(self):
        tag_name = 'bs_test_instance'
        result = self.tag_manager.get_tag_by_name(tag_name, mask=self.test_mask)
        args = (tag_name,)
        self.assertEqual(tag_name, result[0].get('name'))
        self.assert_called_with('SoftLayer_Tag', 'getTagByTagName', mask=self.test_mask, args=args)

    def test_taggable_by_type_main(self):
        result = self.tag_manager.taggable_by_type("HARDWARE")
        self.assertEqual("SoftLayer_Hardware", result[0].get('resourceType'))
        self.assert_called_with('SoftLayer_Search', 'advancedSearch', args=('_objectType:SoftLayer_Hardware',))

    def test_taggable_by_type_ticket(self):
        mock = self.set_mock('SoftLayer_Search', 'advancedSearch')
        mock.return_value = [
            {
                "resourceType": "SoftLayer_Ticket",
                "resource": {
                    "domain": "vmware.test.com",
                }
            }
        ]

        result = self.tag_manager.taggable_by_type("TICKET")
        self.assertEqual("SoftLayer_Ticket", result[0].get('resourceType'))
        self.assert_called_with('SoftLayer_Search', 'advancedSearch',
                                args=('_objectType:SoftLayer_Ticket status.name: open',))

    def test_taggable_by_type_image_template(self):
        result = self.tag_manager.taggable_by_type("IMAGE_TEMPLATE")
        self.assertEqual("Virtual_Guest_Block_Device_Template_Group", result[0].get('resourceType'))
        self.assert_called_with('SoftLayer_Account', 'getPrivateBlockDeviceTemplateGroups')

    def test_taggable_by_type_network_subnet(self):
        result = self.tag_manager.taggable_by_type("NETWORK_SUBNET")
        self.assertEqual("Network_Subnet", result[0].get('resourceType'))
        self.assert_called_with('SoftLayer_Account', 'getSubnets')

    def test_type_to_service(self):
        in_out = [
            {'input': 'ACCOUNT_DOCUMENT', 'output': None},
            {'input': 'APPLICATION_DELIVERY_CONTROLLER', 'output': 'Network_Application_Delivery_Controller'},
            {'input': 'GUEST', 'output': 'Virtual_Guest'},
            {'input': 'DEDICATED_HOST', 'output': 'Virtual_DedicatedHost'},
            {'input': 'IMAGE_TEMPLATE', 'output': 'Virtual_Guest_Block_Device_Template_Group'},
            {'input': 'HARDWARE', 'output': 'Hardware'},
            {'input': 'NETWORK_VLAN', 'output': 'Network_Vlan'},
        ]

        for test in in_out:
            result = self.tag_manager.type_to_service(test.get('input'))
            self.assertEqual(test.get('output'), result)

    def test_get_resource_name(self):
        resource = {
            'primaryIpAddress': '4.4.4.4',
            'vlanNumber': '12345',
            'name': 'testName',
            'subject': 'TEST SUBJECT',
            'networkIdentifier': '127.0.0.1',
            'fullyQualifiedDomainName': 'test.test.com'
        }
        in_out = [
            {'input': 'NETWORK_VLAN_FIREWALL', 'output': resource.get('primaryIpAddress')},
            {'input': 'NETWORK_VLAN', 'output': "{} ({})".format(resource.get('vlanNumber'), resource.get('name'))},
            {'input': 'IMAGE_TEMPLATE', 'output': resource.get('name')},
            {'input': 'APPLICATION_DELIVERY_CONTROLLER', 'output': resource.get('name')},
            {'input': 'TICKET', 'output': resource.get('subjet')},
            {'input': 'NETWORK_SUBNET', 'output': resource.get('networkIdentifier')},
            {'input': 'HARDWARE', 'output': resource.get('fullyQualifiedDomainName')},
        ]

        for test in in_out:
            result = self.tag_manager.get_resource_name(resource, test.get('input'))
            self.assertEqual(test.get('output'), result)
