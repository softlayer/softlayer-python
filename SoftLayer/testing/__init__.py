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
from SoftLayer.testing import fixture_client

from click.testing import CliRunner

FixtureClient = fixture_client.FixtureClient
FIXTURE_PATH = os.path.abspath(os.path.join(__file__, '..', 'fixtures'))


def run_command(args=None,
                env=None,
                environment=None,
                fixtures=True,
                fmt='json'):

    runner = CliRunner()
    if fixtures:
        args.insert(0, '--fixtures')
    args.insert(0, '--format=%s' % fmt)

    return runner.invoke(core.cli, args=args, env=env, obj=environment)


class TestCase(unittest.TestCase):
    """ Testcase class with PEP-8 compatable method names """

    def set_up(self):
        """ aliased from setUp """
        pass

    def tear_down(self):
        """ aliased from tearDown """
        pass

    def setUp(self):  # NOQA
        return self.set_up()

    def tearDown(self):  # NOQA
        return self.tear_down()

__all__ = ['unittest', 'FixtureClient']
