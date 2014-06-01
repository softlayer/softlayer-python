"""
    SoftLayer.tests.CLI.modules.help_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.tests import TestCase
from SoftLayer.CLI.modules import help
from SoftLayer.CLI.environment import Environment


class HelpTests(TestCase):
    def test_help(self):
        command = help.Show(env=Environment())

        output = command.execute({'<module>': None, '<command>': None})
        self.assertTrue('usage: sl help' in output)

        output = command.execute({'<module>': 'help', '<command>': None})
        self.assertTrue('usage: sl help' in output)

        output = command.execute({'<module>': 'server', '<command>': 'list'})
        self.assertTrue('usage: sl server list' in output)
