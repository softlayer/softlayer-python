"""
    SoftLayer.tests.CLI.modules.config_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
import os
import sys
import tempfile

from unittest import mock as mock

import SoftLayer
from SoftLayer import auth
from SoftLayer.CLI.config import setup as config
from SoftLayer.CLI import exceptions
from SoftLayer import consts
from SoftLayer import testing
from SoftLayer import transports


class TestHelpShow(testing.TestCase):

    def set_up(self):
        transport = transports.XmlRpcTransport(endpoint_url='http://endpoint-url',)
        self.env.client = SoftLayer.BaseClient(
            transport=transport,
            auth=auth.BasicAuthentication('username', 'api-key'))

    def test_show(self):
        result = self.run_command(['config', 'show'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         {'Username': 'username',
                          'API Key': 'api-key',
                          'Endpoint URL': 'http://endpoint-url',
                          'Timeout': 'not set'})


class TestHelpSetup(testing.TestCase):

    def set_up(self):
        super(TestHelpSetup, self).set_up()

        # NOTE(kmcdonald): since the endpoint_url is changed with the client
        # in these commands, we need to ensure that a fixtured transport is
        # used.
        transport = testing.MockableTransport(SoftLayer.FixtureTransport())
        self.env.client = SoftLayer.BaseClient(transport=transport)
        self.config_file = "./test_config_file"

    def tearDown(self):
        # Windows doesn't let you write and read from temp files
        # So use a real file instead.
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

    @mock.patch('SoftLayer.Client')
    @mock.patch('SoftLayer.CLI.formatting.confirm')
    @mock.patch('SoftLayer.CLI.environment.Environment.getpass')
    @mock.patch('SoftLayer.CLI.environment.Environment.input')
    def test_setup(self, mocked_input, getpass, confirm_mock, client):
        client.return_value = self.env.client
        if(sys.platform.startswith("win")):
            self.skipTest("Test doesn't work in Windows")
        with tempfile.NamedTemporaryFile() as config_file:
            confirm_mock.return_value = True
            getpass.return_value = 'A' * 64
            mocked_input.side_effect = ['public', 'user', 0]

            result = self.run_command(['--config=%s' % config_file.name, 'config', 'setup'])

            self.assert_no_fail(result)
            self.assertIn('Configuration Updated Successfully', result.output)
            contents = config_file.read().decode("utf-8")

            self.assertIn('[softlayer]', contents)
            self.assertIn('username = user', contents)
            self.assertIn('api_key = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', contents)
            self.assertIn('endpoint_url = %s' % consts.API_PUBLIC_ENDPOINT, contents)

    @mock.patch('SoftLayer.Client')
    @mock.patch('SoftLayer.CLI.formatting.confirm')
    @mock.patch('SoftLayer.CLI.environment.Environment.getpass')
    @mock.patch('SoftLayer.CLI.environment.Environment.input')
    def test_setup_float_timeout(self, mocked_input, getpass, confirm_mock, client):
        client.return_value = self.env.client
        confirm_mock.return_value = True
        getpass.return_value = 'A' * 64
        mocked_input.side_effect = ['public', 'user', 10.0]

        result = self.run_command(['--config=%s' % self.config_file, 'config', 'setup'])

        self.assert_no_fail(result)
        self.assertIn('Configuration Updated Successfully', result.output)

        with open(self.config_file, 'r') as config_file:
            contents = config_file.read()
            self.assertIn('[softlayer]', contents)
            self.assertIn('username = user', contents)
            self.assertIn('api_key = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', contents)
            self.assertIn('endpoint_url = %s' % consts.API_PUBLIC_ENDPOINT, contents)
            self.assertNotIn('timeout = 10.0\n', contents)
            self.assertIn('timeout = 10\n', contents)

    @mock.patch('SoftLayer.Client')
    @mock.patch('SoftLayer.CLI.formatting.confirm')
    @mock.patch('SoftLayer.CLI.environment.Environment.getpass')
    @mock.patch('SoftLayer.CLI.environment.Environment.input')
    def test_setup_cancel(self, mocked_input, getpass, confirm_mock, client):
        client.return_value = self.env.client
        with tempfile.NamedTemporaryFile() as config_file:
            confirm_mock.return_value = False
            getpass.return_value = 'A' * 64
            mocked_input.side_effect = ['public', 'user', 0]

            result = self.run_command(['--config=%s' % config_file.name, 'config', 'setup'])
            self.assertEqual(result.exit_code, 2)
            self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('SoftLayer.CLI.environment.Environment.getpass')
    @mock.patch('SoftLayer.CLI.environment.Environment.input')
    def test_github_1074(self, mocked_input, getpass):
        """Tests to make sure directly using an endpoint works"""
        mocked_input.side_effect = ['test-endpoint']
        endpoint_url = config.get_endpoint_url(self.env)
        self.assertEqual(endpoint_url, 'test-endpoint')

    @mock.patch('SoftLayer.CLI.environment.Environment.getpass')
    @mock.patch('SoftLayer.CLI.environment.Environment.input')
    def test_get_endpoint(self, mocked_input, getpass):
        """Tests to make sure directly using an endpoint works"""
        mocked_input.side_effect = ['private', 'custom', 'test.com', 'public', 'test-endpoint']

        # private
        endpoint_url = config.get_endpoint_url(self.env)
        self.assertEqual(endpoint_url, consts.API_PRIVATE_ENDPOINT)

        # custom - test.com
        endpoint_url = config.get_endpoint_url(self.env)
        self.assertEqual(endpoint_url, 'test.com')

        # public
        endpoint_url = config.get_endpoint_url(self.env)
        self.assertEqual(endpoint_url, consts.API_PUBLIC_ENDPOINT)

        # test-endpoint
        endpoint_url = config.get_endpoint_url(self.env)
        self.assertEqual(endpoint_url, 'test-endpoint')

    @mock.patch('SoftLayer.CLI.environment.Environment.input')
    @mock.patch('SoftLayer.CLI.config.setup.get_sso_url')
    @mock.patch('SoftLayer.CLI.config.setup.get_accounts')
    @mock.patch('SoftLayer.API.IAMClient.authenticate_with_passcode')
    @mock.patch('SoftLayer.API.IAMClient.refresh_iam_token')
    @mock.patch('SoftLayer.API.IAMClient.call')
    def test_sso_login(self, api_call, token, passcode, get_accounts, get_sso_url, mocked_input):
        """Tests to make sure directly using an endpoint works"""
        mocked_input.side_effect = ['n', '123qweasd']
        get_sso_url.return_value = "https://test.com/"
        get_accounts.return_value = {"account_id": 12345, "ims_id": 5555}
        passcode.return_value = {"access_token": "aassddffggh", "refresh_token": "qqqqqqq"}
        token.return_value = {"access_token": "zzzzzz", "refresh_token": "fffffff"}
        test_key = "zz112233"
        user_object_1 = {
            "apiAuthenticationKeys": [{"authenticationKey": test_key}],
            "username": "testerson",
            "id": 99}
        api_call.side_effect = [user_object_1]

        user, apikey = config.sso_login(self.env)
        self.assertEqual("testerson", user)
        self.assertEqual(test_key, apikey)
