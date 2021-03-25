"""
    SoftLayer.tests.CLI.modules.config_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
import sys
import tempfile

import mock

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
