import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA
from mock import patch
from argparse import ArgumentParser


import SoftLayer.CLI as cli

if sys.version_info >= (3,):
    raw_input_path = 'builtins.input'
else:
    raw_input_path = '__builtin__.raw_input'


class PromptTests(unittest.TestCase):

    @patch(raw_input_path)
    def test_invalid_response(self, raw_input_mock):
        raw_input_mock.return_value = 'y'
        result = cli.helpers.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertFalse(result)

        raw_input_mock.return_value = 'wakakwakwaka'
        result = cli.helpers.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertFalse(result)

        raw_input_mock.return_value = ''
        result = cli.helpers.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertEqual(result, None)

    @patch(raw_input_path)
    def test_valid_response(self, raw_input_mock):
        raw_input_mock.return_value = 'n'
        result = cli.helpers.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertTrue(result)

        raw_input_mock.return_value = 'N'
        result = cli.helpers.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertTrue(result)

    @patch(raw_input_path)
    def test_do_or_die(self, raw_input_mock):
        confirmed = '37347373737'
        raw_input_mock.return_value = confirmed
        result = cli.no_going_back(confirmed)
        self.assertTrue(result)

        confirmed = None
        raw_input_mock.return_value = ''
        result = cli.no_going_back(confirmed)
        self.assertFalse(result)

    def test_clirunnable_exercise(self):
        res = cli.CLIRunnable.add_additional_args(None)
        self.assertEqual(res, None)
        res = cli.CLIRunnable.execute(None, None)
        self.assertEqual(res, None)

    @patch(raw_input_path)
    def test_confirmation(self, raw_input_mock):
        raw_input_mock.return_value = 'Y'
        res = cli.confirm(allow_empty=False, default=False)
        self.assertTrue(res)

        raw_input_mock.return_value = 'N'
        res = cli.confirm(allow_empty=False, default=False)
        self.assertFalse(res)

        raw_input_mock.return_value = ''
        res = cli.confirm(allow_empty=True, default=True)
        self.assertTrue(res)

    def test_add_really_argument(self):
        parser = ArgumentParser()
        cli.helpers.add_really_argument(parser)
        args = parser.parse_args(['--really'])
        self.assertTrue(args.really)


class CLIAbortTests(unittest.TestCase):
    def test_init(self):
        e = cli.helpers.CLIAbort()
        self.assertEqual(2, e.code)
        self.assertIsInstance(e, cli.helpers.CLIHalt)


class EnvironmentTests(unittest.TestCase):

    def test_plugin_list(self):
        env = cli.environment.Environment()
        actions = env.plugin_list()
        self.assertIn('cci', actions)
        self.assertIn('dns', actions)


class CLIRunnableTypeTests(unittest.TestCase):

    def test_runnable_type(self):
        cli.environment.CLIRunnableType.env = cli.environment.Environment()

        class TestCommand(cli.CLIRunnable):
            action = 'test'
        self.assertEqual(
            cli.environment.CLIRunnableType.env.plugins,
            {'helper_tests': {'test': TestCommand}})
