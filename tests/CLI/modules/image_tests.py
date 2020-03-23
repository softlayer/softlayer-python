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
