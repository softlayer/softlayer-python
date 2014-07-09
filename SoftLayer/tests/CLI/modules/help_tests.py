"""
    SoftLayer.tests.CLI.modules.help_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.CLI import environment
from SoftLayer.CLI.modules import help
from SoftLayer import testing


class HelpTests(testing.TestCase):
    def test_help(self):
        command = help.Show(env=environment.Environment())

        output = command.execute({'<module>': None, '<command>': None})
        self.assertTrue('usage: sl help' in output)

        output = command.execute({'<module>': 'help', '<command>': None})
        self.assertTrue('usage: sl help' in output)

        output = command.execute({'<module>': 'server', '<command>': 'list'})
        self.assertTrue('usage: sl server list' in output)
