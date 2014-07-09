"""
    SoftLayer.tests.CLI.modules.config_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import tempfile

import mock

from SoftLayer import auth
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI.modules import config
from SoftLayer import consts
from SoftLayer import testing


class TestHelpShow(testing.TestCase):
    def set_up(self):
        client = mock.MagicMock()
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
        self.assertEqual(expected, formatting.format_output(output, 'python'))


class TestHelpSetup(testing.TestCase):
    def set_up(self):
        client = testing.FixtureClient()
        client.auth = auth.BasicAuthentication('default-user', 'default-key')
        client.endpoint_url = 'default-endpoint-url'
        client.timeout = 10
        self.client = client
        self.env = mock.MagicMock()

    @mock.patch('SoftLayer.CLI.formatting.confirm')
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
            self.assertTrue('endpoint_url = %s' % consts.API_PUBLIC_ENDPOINT
                            in contents)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_setup_cancel(self, confirm_mock):
        with tempfile.NamedTemporaryFile() as config_file:
            confirm_mock.return_value = False
            self.env.getpass.return_value = 'A' * 64
            self.env.input.side_effect = ['user', 'public']

            command = config.Setup(client=self.client, env=self.env)
            self.assertRaises(exceptions.CLIAbort,
                              command.execute, {'--config': config_file.name})

    def test_get_user_input_private(self):
        command = config.Setup(client=self.client, env=self.env)
        # get_user_input
        self.env.getpass.return_value = 'A' * 64
        self.env.input.side_effect = ['user', 'private']

        username, secret, endpoint_url, timeout = command.get_user_input()

        self.assertEqual(username, 'user')
        self.assertEqual(secret, 'A' * 64)
        self.assertEqual(endpoint_url, consts.API_PRIVATE_ENDPOINT)
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

        self.assertEqual(endpoint_url, consts.API_PUBLIC_ENDPOINT)
