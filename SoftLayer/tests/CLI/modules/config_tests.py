"""
    SoftLayer.tests.CLI.modules.config_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from mock import MagicMock, patch
import tempfile

from SoftLayer import API_PUBLIC_ENDPOINT, API_PRIVATE_ENDPOINT
from SoftLayer.auth import BasicAuthentication
from SoftLayer.tests import unittest, FixtureClient
from SoftLayer.CLI.modules import config
from SoftLayer.CLI.helpers import format_output
from SoftLayer.CLI.exceptions import CLIAbort


class TestHelpShow(unittest.TestCase):
    def setUp(self):
        client = MagicMock()
        client.auth.username = 'user'
        client.auth.api_key = '12345'
        client.endpoint_url = 'https://some/endpoint'
        client.timeout = 10
        self.client = client

    def test_show(self):
        command = config.Show(client=self.client)

        output = command.execute({})

        expected = {'Username': self.client.auth.username,
                    'Endpoint URL': self.client.endpoint_url,
                    'API Key': self.client.auth.api_key,
                    'Timeout': self.client.timeout}
        self.assertEqual(expected, format_output(output, 'python'))


class TestHelpSetup(unittest.TestCase):
    def setUp(self):
        client = FixtureClient()
        client.auth = BasicAuthentication('default-user', 'default-key')
        client.endpoint_url = 'default-endpoint-url'
        client.timeout = 10
        self.client = client
        self.env = MagicMock()

    @patch('SoftLayer.CLI.modules.config.confirm')
    def test_setup(self, confirm_mock):
        with tempfile.NamedTemporaryFile() as config_file:
            confirm_mock.return_value = True
            self.env.getpass.return_value = 'A' * 64
            self.env.input.side_effect = ['user', 'public']

            command = config.Setup(client=self.client, env=self.env)
            output = command.execute({'--config': config_file.name})

            self.assertEqual('Configuration Updated Successfully', output)
            contents = config_file.read().decode("utf-8")
            self.assertTrue('[softlayer]' in contents)
            self.assertTrue('username = user' in contents)
            self.assertTrue('api_key = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAA' in contents)
            self.assertTrue('endpoint_url = %s' % API_PUBLIC_ENDPOINT
                            in contents)

    @patch('SoftLayer.CLI.modules.config.confirm')
    def test_setup_cancel(self, confirm_mock):
        with tempfile.NamedTemporaryFile() as config_file:
            confirm_mock.return_value = False
            self.env.getpass.return_value = 'A' * 64
            self.env.input.side_effect = ['user', 'public']

            command = config.Setup(client=self.client, env=self.env)
            self.assertRaises(CLIAbort,
                              command.execute, {'--config': config_file.name})

    def test_get_user_input_private(self):
        command = config.Setup(client=self.client, env=self.env)
        # get_user_input
        self.env.getpass.return_value = 'A' * 64
        self.env.input.side_effect = ['user', 'private']

        username, secret, endpoint_url, timeout = command.get_user_input()

        self.assertEqual(username, 'user')
        self.assertEqual(secret, 'A' * 64)
        self.assertEqual(endpoint_url, API_PRIVATE_ENDPOINT)
        self.assertEqual(timeout, 10)

    def test_get_user_input_custom(self):
        command = config.Setup(client=self.client, env=self.env)
        # get_user_input
        self.env.getpass.return_value = 'A' * 64
        self.env.input.side_effect = ['user', 'custom', 'custom-endpoint']

        _, _, endpoint_url, _ = command.get_user_input()

        self.assertEqual(endpoint_url, 'custom-endpoint')

    def test_get_user_input_default(self):
        command = config.Setup(client=self.client, env=self.env)
        # get_user_input
        self.env.getpass.return_value = 'A' * 64
        self.env.input.side_effect = ['user', '']

        _, _, endpoint_url, _ = command.get_user_input()

        self.assertEqual(endpoint_url, API_PUBLIC_ENDPOINT)
