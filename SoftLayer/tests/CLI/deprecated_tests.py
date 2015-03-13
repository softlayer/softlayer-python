"""
    SoftLayer.tests.CLI.deprecated_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import click

from SoftLayer.CLI import deprecated
from SoftLayer import testing


class EnvironmentTests(testing.TestCase):

    def test_main(self):
        runner = click.testing.CliRunner()
        result = runner.invoke(deprecated.main)

        self.assertEquals(result.exit_code, -1)
        self.assertIn("ERROR: Use the 'slcli' command instead.", result.output)
