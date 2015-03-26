"""
    SoftLayer.tests.CLI.deprecated_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

from SoftLayer.CLI import deprecated
from SoftLayer import testing
from SoftLayer import utils


class EnvironmentTests(testing.TestCase):

    def test_main(self):

        with mock.patch('sys.stderr', new=utils.StringIO()) as fake_out:
            ex = self.assertRaises(SystemExit, deprecated.main)
            self.assertEqual(ex.code, -1)

            self.assertIn("ERROR: Use the 'slcli' command instead.",
                          fake_out.getvalue())

    def test_with_args(self):
        with mock.patch('sys.stderr', new=utils.StringIO()) as fake_out:
            with mock.patch('sys.argv', new=['sl', 'module', 'subcommand']):
                ex = self.assertRaises(SystemExit, deprecated.main)
                self.assertEqual(ex.code, -1)

                self.assertIn("ERROR: Use the 'slcli' command instead.",
                              fake_out.getvalue())
