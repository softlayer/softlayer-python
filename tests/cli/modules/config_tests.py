"""
    softlayer.tests.cli.modules.config_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
import tempfile

import mock

from softlayer.cli.config import setup as config
from softlayer.cli import exceptions
from softlayer import consts
from softlayer import testing


class TestHelpShow(testing.TestCase):

    def test_show(self):
        result = self.run_command(['config', 'show'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output),
                         {'Username': 'default-user',
                          'API Key': 'default-key',
                          'Endpoint URL': 'default-endpoint-url',
                          'Timeout': 10.0})


class TestHelpSetup(testing.TestCase):

    @mock.patch('softlayer.cli.formatting.confirm')
    @mock.patch('softlayer.cli.environment.Environment.getpass')
    @mock.patch('softlayer.cli.environment.Environment.input')
    def test_setup(self, input, getpass, confirm_mock):
        with tempfile.NamedTemporaryFile() as config_file:
            confirm_mock.return_value = True
            getpass.return_value = 'A' * 64
            input.side_effect = ['user', 'public']

            result = self.run_command(['--config=%s' % config_file.name,
                                       'config', 'setup'])

            self.assertEqual(result.exit_code, 0)
            self.assertTrue('Configuration Updated Successfully'
                            in result.output)
            contents = config_file.read().decode("utf-8")
            self.assertTrue('[softlayer]' in contents)
            self.assertTrue('username = user' in contents)
            self.assertTrue('api_key = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAA' in contents)
            self.assertTrue('endpoint_url = %s' % consts.API_PUBLIC_ENDPOINT
                            in contents)

    @mock.patch('softlayer.cli.formatting.confirm')
    @mock.patch('softlayer.cli.environment.Environment.getpass')
    @mock.patch('softlayer.cli.environment.Environment.input')
    def test_setup_cancel(self, input, getpass, confirm_mock):
        with tempfile.NamedTemporaryFile() as config_file:
            confirm_mock.return_value = False
            getpass.return_value = 'A' * 64
            input.side_effect = ['user', 'public']

            result = self.run_command(['--config=%s' % config_file.name,
                                       'config', 'setup'])

            self.assertEqual(result.exit_code, 2)
            self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('softlayer.cli.environment.Environment.getpass')
    @mock.patch('softlayer.cli.environment.Environment.input')
    def test_get_user_input_private(self, input, getpass):
        getpass.return_value = 'A' * 64
        input.side_effect = ['user', 'private']

        username, secret, endpoint_url, timeout = (
            config.get_user_input(self.env))

        self.assertEqual(username, 'user')
        self.assertEqual(secret, 'A' * 64)
        self.assertEqual(endpoint_url, consts.API_PRIVATE_ENDPOINT)
        self.assertEqual(timeout, 10)

    @mock.patch('softlayer.cli.environment.Environment.getpass')
    @mock.patch('softlayer.cli.environment.Environment.input')
    def test_get_user_input_custom(self, input, getpass):
        getpass.return_value = 'A' * 64
        input.side_effect = ['user', 'custom', 'custom-endpoint']

        _, _, endpoint_url, _ = config.get_user_input(self.env)

        self.assertEqual(endpoint_url, 'custom-endpoint')

    @mock.patch('softlayer.cli.environment.Environment.getpass')
    @mock.patch('softlayer.cli.environment.Environment.input')
    def test_get_user_input_default(self, input, getpass):
        self.env.getpass.return_value = 'A' * 64
        self.env.input.side_effect = ['user', '']

        _, _, endpoint_url, _ = config.get_user_input(self.env)

        self.assertEqual(endpoint_url, consts.API_PUBLIC_ENDPOINT)
