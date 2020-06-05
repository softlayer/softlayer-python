"""
    SoftLayer.tests.CLI.modules.tag_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for the user cli command
"""
import mock

from SoftLayer import testing
from SoftLayer.managers.tags import TagManager


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

    @mock.patch('SoftLayer.CLI.tags.set.click')
    def test_set_tags(self, click):
        result = self.run_command(['tags', 'set', '--tags=tag1,tag2', '--key-name=GUEST', '--resource-id=100'])
        click.secho.assert_called_with('Set tags successfully', fg='green')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Tag', 'setTags',
                                args=("tag1,tag2", "GUEST", 100), )

    @mock.patch('SoftLayer.CLI.tags.set.click')
    def test_set_tags_failure(self, click):
        mock = self.set_mock('SoftLayer_Tag', 'setTags')
        mock.return_value = False
        result = self.run_command(['tags', 'set', '--tags=tag1,tag2', '--key-name=GUEST', '--resource-id=100'])
        click.secho.assert_called_with('Failed to set tags', fg='red')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Tag', 'setTags',
                                args=("tag1,tag2", "GUEST", 100), )

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
        result = self.run_command(['tags', 'delete', '--name="test"'])
        self.assert_no_fail(result)

    def test_deleteTags_by_id(self):
        result = self.run_command(['tags', 'delete', '-id=123456'])
        self.assert_no_fail(result)
