"""
    SoftLayer.testing
    ~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
# Disable pylint import error and too many methods error
# pylint: disable=F0401,R0904
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import os.path

from SoftLayer.CLI import core
from SoftLayer.CLI import environment
from SoftLayer.testing import fixture_client

from click import testing

FixtureClient = fixture_client.FixtureClient
FIXTURE_PATH = os.path.abspath(os.path.join(__file__, '..', 'fixtures'))


class TestCase(unittest.TestCase):
    """Testcase class with PEP-8 compatable method names."""

    def set_up(self):
        """Aliased from setUp."""
        pass

    def tear_down(self):
        """Aliased from tearDown."""
        pass

    def setUp(self):  # NOQA
        self.env = environment.Environment()
        self.client = FixtureClient()
        self.env.client = core.CliClient(self.client)
        return self.set_up()

    def tearDown(self):  # NOQA
        return self.tear_down()

    def run_command(self,
                    args=None,
                    env=None,
                    fixtures=True,
                    fmt='json'):

        runner = testing.CliRunner()
        if fixtures:
            args.insert(0, '--fixtures')
        args.insert(0, '--format=%s' % fmt)

        return runner.invoke(core.cli, args=args, obj=env or self.env)

__all__ = ['unittest', 'FixtureClient']
