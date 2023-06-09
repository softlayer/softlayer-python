"""
    SoftLayer.tests.CLI.modules.image_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer import testing


class ImageTests(testing.TestCase):

    def test_detail(self):
        result = self.run_command(['image', 'detail', '100'])
        self.assert_no_fail(result)

    def test_delete(self):
        result = self.run_command(['image', 'delete', '100'])
        self.assert_no_fail(result)

    def test_edit_note(self):
        result = self.run_command(['image', 'edit', '100', '--note=test'])
        self.assert_no_fail(result)

    def test_edit_name(self):
        result = self.run_command(['image', 'edit', '100', '--name=test'])
        self.assert_no_fail(result)

    def test_edit_tag(self):
        result = self.run_command(['image', 'edit', '100', '--tag=test'])
        self.assert_no_fail(result)

    def test_import(self):
        result = self.run_command(['image', 'import', '100', 'swift://test'])
        self.assert_no_fail(result)

    def test_export(self):
        result = self.run_command(['image', 'export', '100', 'swift://test'])
        self.assert_no_fail(result)

    def test_list(self):
        result = self.run_command(['image', 'list'])
        self.assert_no_fail(result)

    def test_datacenter_add(self):
        result = self.run_command(['image', 'datacenter', '100', '--add', 'ams01'])
        self.assert_no_fail(result)

    def test_datacenter_remove(self):
        result = self.run_command(['image', 'datacenter', '100', '--remove', 'ams01'])
        self.assert_no_fail(result)

    def test_datacenter_remove_fails(self):
        result = self.run_command(['image', 'datacenter', '100', '--remove'])
        self.assertEqual(2, result.exit_code)

    def test_share(self):
        result = self.run_command(['image', 'share', '123456', '--account-id', '654321'])
        self.assert_no_fail(result)
        self.assertIn("Image template 123456 was shared to account 654321.", result.output)

    def test_share_without_id(self):
        result = self.run_command(['image', 'share'])
        self.assertEqual(2, result.exit_code)
        self.assertIn("Error: Missing argument 'IDENTIFIER'.", result.output)

    def test_share_without_id_account(self):
        result = self.run_command(['image', 'share', "123456"])
        self.assertEqual(2, result.exit_code)
        self.assertIn("Error: Missing option '--account-id'.", result.output)

    def test_deny_share(self):
        result = self.run_command(['image', 'share-deny', '123456', '--account-id', '654321'])
        self.assert_no_fail(result)
        self.assertIn("Image template 123456 was deny shared to account 654321.", result.output)

    def test_deny_share_without_id(self):
        result = self.run_command(['image', 'share-deny'])
        self.assertEqual(2, result.exit_code)
        self.assertIn("Error: Missing argument 'IDENTIFIER'.", result.output)

    def test_deny_share_without_id_account(self):
        result = self.run_command(['image', 'share-deny', "123456"])
        self.assertEqual(2, result.exit_code)
        self.assertIn("Error: Missing option '--account-id'.", result.output)
