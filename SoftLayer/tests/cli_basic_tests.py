import SoftLayer
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest
from mock import patch
import SoftLayer.CLI
import prettytable

if sys.version_info >= (3,):
    raw_input_path = 'builtins.input'
else:
    raw_input_path = '__builtin__.raw_input'


class PromptTests(unittest.TestCase):

    @patch(raw_input_path)
    def test_invalid_response(self, raw_input_mock):
        raw_input_mock.return_value = 'y'
        result = SoftLayer.CLI.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertFalse(result)

        raw_input_mock.return_value = 'wakakwakwaka'
        result = SoftLayer.CLI.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertFalse(result)

        raw_input_mock.return_value = ''
        result = SoftLayer.CLI.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertEqual(result, None)

    @patch(raw_input_path)
    def test_valid_response(self, raw_input_mock):
        raw_input_mock.return_value = 'n'
        result = SoftLayer.CLI.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertTrue(result)

        raw_input_mock.return_value = 'N'
        result = SoftLayer.CLI.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertTrue(result)

    def test_prettytable_helper(self):
        t = SoftLayer.CLI.Table(['one', 'two'])
        self.assertEqual(t.horizontal_char, '.')
        self.assertEqual(t.vertical_char, ':')
        self.assertEqual(t.junction_char, ':')

    @patch(raw_input_path)
    def test_do_or_die(self, raw_input_mock):
        confirmed = '37347373737'
        raw_input_mock.return_value = confirmed
        result = SoftLayer.CLI.no_going_back(confirmed)
        self.assertTrue(result)

        confirmed = None
        raw_input_mock.return_value = ''
        result = SoftLayer.CLI.no_going_back(confirmed)
        self.assertFalse(result)

    def test_clirunnable_exercise(self):
        res = SoftLayer.CLI.CLIRunnable.add_additional_args(None)
        self.assertEqual(res, None)
        res = SoftLayer.CLI.CLIRunnable.execute(None, None)
        self.assertEqual(res, None)

    @patch(raw_input_path)
    def test_confirmation(self, raw_input_mock):
        raw_input_mock.return_value = 'Y'
        res = SoftLayer.CLI.confirm(allow_empty=False, default=False)
        self.assertTrue(res)

        raw_input_mock.return_value = 'N'
        res = SoftLayer.CLI.confirm(allow_empty=False, default=False)
        self.assertFalse(res)

        raw_input_mock.return_value = ''
        res = SoftLayer.CLI.confirm(allow_empty=True, default=True)
        self.assertTrue(res)

    def test_no_tty(self):
        class fake(object):
            pass
        args = fake()
        args.fmt = 'raw'

        t = SoftLayer.CLI.Table(['nothing'])
        t.align['nothing'] = 'c'
        t.hrules = prettytable.FRAME
        ret = SoftLayer.CLI.format_output(t, args)

        self.assertFalse(ret.border)
        self.assertFalse(ret.header)
        self.assertNotEqual(ret.hrules, t.hrules)
        self.assertNotEqual(ret.align, t.align)

    def test_prettytable(self):
        class fake(object):
            pass
        args = fake()
        args.fmt = 'table'

        t = SoftLayer.CLI.Table(['nothing'])
        t.align['nothing'] = 'c'
        t.hrules = prettytable.FRAME
        ret = SoftLayer.CLI.format_output(t, args)

        self.assertEqual(ret.hrules, t.hrules)
        self.assertEqual(ret.align, t.align)
