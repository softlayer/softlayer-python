"""
    SoftLayer.tests.CLI.modules.tag_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for the user cli command
"""
from unittest import mock as mock

from SoftLayer.exceptions import SoftLayerAPIError
from SoftLayer import testing


class TagCLITests(testing.TestCase):

    def test_list(self):
        result = self.run_command(['tags', 'list'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Tag', 'getUnattachedTagsForCurrentUser')
        self.assert_called_with('SoftLayer_Tag', 'getAttachedTagsForCurrentUser')
        self.assertIn('coreos', result.output)

    def test_list_detail(self):
        result = self.run_command(['tags', 'list', '-d'])
        self.assert_no_fail(result)
        self.assertIn('"vs-test1.test.sftlyr.ws', result.output)  # From fixtures/virutal_guest.getObject
        # self.assert_called_with('SoftLayer_Tag', 'getUnattachedTagsForCurrentUser')
        self.assert_called_with('SoftLayer_Tag', 'getAttachedTagsForCurrentUser')
        self.assert_called_with('SoftLayer_Tag', 'getReferences', identifier=1286571)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'getObject', identifier=33488921)

    def test_list_detail_ungettable(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getObject')
        mock.side_effect = SoftLayerAPIError(404, "TEST ERROR")
        result = self.run_command(['tags', 'list', '-d'])
        self.assert_no_fail(result)
        self.assertIn("TEST ERROR", result.output)  # From fixtures/virutal_guest.getObject
        # self.assert_called_with('SoftLayer_Tag', 'getUnattachedTagsForCurrentUser')
        self.assert_called_with('SoftLayer_Tag', 'getAttachedTagsForCurrentUser')
        self.assert_called_with('SoftLayer_Tag', 'getReferences', identifier=1286571)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'getObject', identifier=33488921)

    @mock.patch('SoftLayer.CLI.tags.set.click')
    def test_set_tags(self, click):
        result = self.run_command(['tags', 'set', '--tags=tag1,tag2', '--key-name=GUEST', '--resource-id=100'])
        click.secho.assert_called_with('Set tags successfully', fg='green')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Tag', 'setTags',  args=("tag1,tag2", "GUEST", 100), )

    @mock.patch('SoftLayer.CLI.tags.set.click')
    def test_set_tags_failure(self, click):
        mock = self.set_mock('SoftLayer_Tag', 'setTags')
        mock.return_value = False
        result = self.run_command(['tags', 'set', '--tags=tag1,tag2', '--key-name=GUEST', '--resource-id=100'])
        click.secho.assert_called_with('Failed to set tags', fg='red')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Tag', 'setTags', args=("tag1,tag2", "GUEST", 100), )

    def test_details_by_name(self):
        tag_name = 'bs_test_instance'
        result = self.run_command(['tags', 'details', tag_name])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Tag', 'getTagByTagName', args=(tag_name,))

    def test_details_by_id(self):
        tag_id = '1286571'
        result = self.run_command(['tags', 'details', tag_id])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Tag', 'getObject', identifier=tag_id)

    def test_deleteTags_by_name(self):
        result = self.run_command(['tags', 'delete', 'test'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Tag', 'deleteTag', args=('test',))

    def test_deleteTags_by_id(self):
        result = self.run_command(['tags', 'delete', '123456'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Tag', 'getObject', identifier='123456')
        self.assert_called_with('SoftLayer_Tag', 'deleteTag', args=('bs_test_instance',))

    def test_deleteTags_by_number_name(self):
        result = self.run_command(['tags', 'delete', '123456', '--name'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Tag', 'deleteTag', args=('123456',))

    @mock.patch('SoftLayer.CLI.tags.delete.click')
    def test_deleteTags_fail(self, click):
        mock = self.set_mock('SoftLayer_Tag', 'deleteTag')
        mock.return_value = False
        result = self.run_command(['tags', 'delete', '123456', '--name'])
        click.secho.assert_called_with('Failed to remove tag 123456', fg='red')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Tag', 'deleteTag', args=('123456',))

    def test_taggable(self):
        result = self.run_command(['tags', 'taggable'])
        self.assert_no_fail(result)
        self.assertIn('"host14.vmware.test.com', result.output)
        self.assert_called_with('SoftLayer_Tag', 'getAllTagTypes')
        self.assert_called_with('SoftLayer_Search', 'advancedSearch', args=('_objectType:SoftLayer_Hardware',))

    def test_cleanup(self):
        result = self.run_command(['tags', 'cleanup'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Tag', 'getUnattachedTagsForCurrentUser')
        self.assert_called_with('SoftLayer_Tag', 'deleteTag', args=('coreos',))

    def test_cleanup_dry(self):
        result = self.run_command(['tags', 'cleanup', '-d'])
        self.assert_no_fail(result)
        self.assertIn('(Dry Run)', result.output)
        self.assert_called_with('SoftLayer_Tag', 'getUnattachedTagsForCurrentUser')
        self.assertEqual([], self.calls(service='SoftLayer_Tag',  method='deleteTag'))
