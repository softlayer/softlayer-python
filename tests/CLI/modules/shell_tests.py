"""
    SoftLayer.tests.CLI.modules.shell_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing

import mock


class ShellTests(testing.TestCase):
    @mock.patch('prompt_toolkit.shortcuts.prompt')
    def test_shell_quit(self, prompt):
        prompt.return_value = "quit"
        result = self.run_command(['shell'])
        self.assertEqual(result.exit_code, 0)
