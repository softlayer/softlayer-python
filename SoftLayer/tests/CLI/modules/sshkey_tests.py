"""
    SoftLayer.tests.CLI.modules.sshkey_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import os.path
import tempfile

import mock

from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI.modules import sshkey
from SoftLayer import testing


class SshKeyTests(testing.TestCase):
    def set_up(self):
        self.client = testing.FixtureClient()

    def test_add_by_option(self):
        service = self.client['Security_Ssh_Key']
        command = sshkey.AddSshKey(client=self.client)
        mock_key = service.getObject()['key']

        output = command.execute({
            '<label>': 'key1',
            '--key': mock_key,
            '--notes': 'my key',
        })

        self.assertEqual(output, 'SSH key added: aa:bb:cc:dd')
        service.createObject.assert_called_with({'notes': 'my key',
                                                 'key': mock_key,
                                                 'label': 'key1'})

    def test_add_by_file(self):
        command = sshkey.AddSshKey(client=self.client)
        path = os.path.join(testing.FIXTURE_PATH, 'id_rsa.pub')

        output = command.execute({
            '<label>': 'key1',
            '--file': path,
        })

        self.assertEqual(output, 'SSH key added: aa:bb:cc:dd')

    def test_remove_key(self):
        command = sshkey.RemoveSshKey(client=self.client)
        command.execute({'<identifier>': '1234',
                         '--really': True})

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_remove_key_fail(self, ngb_mock):
        ngb_mock.return_value = False

        command = sshkey.RemoveSshKey(client=self.client)

        self.assertRaises(exceptions.CLIAbort,
                          command.execute, {'<identifier>': '1234',
                                            '--really': False})

    def test_edit_key(self):
        command = sshkey.EditSshKey(client=self.client)
        output = command.execute({
            '<identifier>': '1234',
            '--label': 'key1',
            '--notes': 'my key',
        })

        self.assertEqual(output, None)
        service = self.client['Security_Ssh_Key']
        service.editObject.assert_called_with({'notes': 'my key',
                                               'label': 'key1'}, id=1234)

    def test_edit_key_fail(self):
        service = self.client['Security_Ssh_Key']
        service.editObject.return_value = False
        command = sshkey.EditSshKey(client=self.client)
        self.assertRaises(exceptions.CLIAbort,
                          command.execute, {'<identifier>': '1234',
                                            '--label': 'key1',
                                            '--notes': 'my key'})

    def test_list_keys(self):
        command = sshkey.ListSshKey(client=self.client)
        output = command.execute({})

        self.assertEqual(formatting.format_output(output, 'python'),
                         [{'notes': '-',
                           'fingerprint': None,
                           'id': '100',
                           'label': 'Test 1'},
                          {'notes': 'my key',
                           'fingerprint': None,
                           'id': '101',
                           'label': 'Test 2'}])

    def test_print_key(self):
        command = sshkey.PrintSshKey(client=self.client)
        output = command.execute({'<identifier>': '1234'})

        self.assertEqual(formatting.format_output(output, 'python'),
                         {'id': 1234, 'label': 'label', 'notes': 'notes'})

    def test_print_key_file(self):
        sshkey_file = tempfile.NamedTemporaryFile()
        service = self.client['Security_Ssh_Key']
        mock_key = service.getObject()['key']
        command = sshkey.PrintSshKey(client=self.client)

        command.execute({'<identifier>': '1234', '--file': sshkey_file.name})

        self.assertEqual(mock_key, sshkey_file.read().decode("utf-8"))
