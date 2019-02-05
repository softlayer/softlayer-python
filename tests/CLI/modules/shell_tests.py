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

    @mock.patch('prompt_toolkit.shortcuts.prompt')
    @mock.patch('shlex.split')
    def test_shell_help(self, prompt, split):
        split.side_effect = [(['help']), (['vs', 'list']), (False), (['quit'])]
        prompt.return_value = "none"
        result = self.run_command(['shell'])
        if split.call_count is not 5:
            raise Exception("Split not called correctly. Count: " + str(split.call_count))
        self.assertEqual(result.exit_code, 1)
