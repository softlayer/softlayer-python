"""
    SoftLayer.tests.CLI.environment_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import click
from unittest import mock as mock

from SoftLayer.CLI import environment
from SoftLayer import testing


@click.command()
def fixture_command():
    pass


class EnvironmentTests(testing.TestCase):

    def set_up(self):
        self.env = environment.Environment()

    def test_list_commands(self):
        self.env.load()
        actions = self.env.list_commands()
        self.assertIn('virtual', actions)
        self.assertIn('dns', actions)

    def test_get_command_invalid(self):
        cmd = self.env.get_command('invalid', 'command')
        self.assertEqual(cmd, None)

    def test_get_command(self):
        fixture_loader = environment.ModuleLoader(
            'tests.CLI.environment_tests',
            'fixture_command',
        )
        self.env.commands = {'fixture:run': fixture_loader}
        command = self.env.get_command('fixture', 'run')
        self.assertIsInstance(command, click.Command)

    @mock.patch('click.prompt')
    def test_input(self, prompt_mock):
        r = self.env.input('input')
        prompt_mock.assert_called_with('input',
                                       default=None,
                                       show_default=True)
        self.assertEqual(prompt_mock(), r)

    @mock.patch('click.prompt')
    def test_getpass(self, prompt_mock):
        r = self.env.getpass('input')
        prompt_mock.assert_called_with('input', default=None, hide_input=True)
        self.assertEqual(prompt_mock(), r)

    @mock.patch('click.prompt')
    @mock.patch('tkinter.Tk')
    def test_getpass_issues1436(self, tk, prompt_mock):
        prompt_mock.return_value = 'àR'
        self.env.getpass('input')
        prompt_mock.assert_called_with('input', default=None, hide_input=True)
        tk.assert_called_with()

    def test_resolve_alias(self):
        self.env.aliases = {'aliasname': 'realname'}
        r = self.env.resolve_alias('aliasname')
        self.assertEqual(r, 'realname')

        r = self.env.resolve_alias('realname')
        self.assertEqual(r, 'realname')

    @mock.patch('click.echo')
    def test_print_unicode(self, echo):
        output = "\u3010TEST\u3011 image"
        # https://docs.python.org/3.6/library/exceptions.html#UnicodeError
        echo.side_effect = [
            UnicodeEncodeError('utf8', output, 0, 1, "Test Exception"),
            output
        ]
        self.env.fout(output)
        self.assertEqual(2, echo.call_count)

    def test_format_output_is_json(self):
        self.env.format = 'jsonraw'
        self.assertTrue(self.env.format_output_is_json())
