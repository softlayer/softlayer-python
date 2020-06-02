"""
    SoftLayer.tests.CLI.modules.tag_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for the user cli command
"""
from SoftLayer.fixtures import SoftLayer_Account as SoftLayer_Account
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
