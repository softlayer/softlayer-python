"""
    SoftLayer.tests.CLI.modules.shell_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing

import tempfile


class ShellTests(testing.TestCase):

    def test_shell_quit(self):
        # Use a file as stdin
        with tempfile.NamedTemporaryFile() as stdin:
            stdin.write(b'exit\n')
            stdin.seek(0)
            result = self.run_command(['shell'], input=stdin)
            self.assertEqual(result.exit_code, 0)

    def test_shell_help(self):
        # Use a file as stdin
        with tempfile.NamedTemporaryFile() as stdin:
            stdin.write(b'help\nexit\n')
            stdin.seek(0)
            result = self.run_command(['shell'], input=stdin)
            self.assertIn('Welcome to the SoftLayer shell.', result.output)
            self.assertEqual(result.exit_code, 0)
