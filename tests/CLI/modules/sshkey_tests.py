"""
    SoftLayer.tests.CLI.modules.sshkey_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
import os.path
import tempfile

import mock

from SoftLayer import testing


class SshKeyTests(testing.TestCase):

    def test_add_by_option(self):
        service = self.client['Security_Ssh_Key']
        mock_key = service.getObject()['key']

        result = self.run_command(['sshkey', 'add', 'key1',
                                   '--key=%s' % mock_key,
                                   '--note=my key'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output),
                         "SSH key added: aa:bb:cc:dd")
        self.assert_called_with('SoftLayer_Security_Ssh_Key', 'createObject',
                                args=({'notes': 'my key',
                                       'key': mock_key,
                                       'label': 'key1'},))

    def test_add_by_file(self):
        path = os.path.join(testing.FIXTURE_PATH, 'id_rsa.pub')

        result = self.run_command(['sshkey', 'add', 'key1',
                                   '--in-file=%s' % path])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output),
                         "SSH key added: aa:bb:cc:dd")
        service = self.client['Security_Ssh_Key']
        mock_key = service.getObject()['key']
        self.assert_called_with('SoftLayer_Security_Ssh_Key', 'createObject',
                                args=({'notes': None,
                                       'key': mock_key,
                                       'label': 'key1'},))

    def test_remove_key(self):
        result = self.run_command(['--really', 'sshkey', 'remove', '1234'])

        self.assertEqual(result.exit_code, 0)
        self.assert_called_with('SoftLayer_Security_Ssh_Key', 'deleteObject',
                                identifier=1234)

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_remove_key_fail(self, ngb_mock):
        ngb_mock.return_value = False
        result = self.run_command(['sshkey', 'remove', '1234'])

        self.assertEqual(result.exit_code, 2)

    def test_edit_key(self):
        result = self.run_command(['sshkey', 'edit', '1234',
                                   '--label=key1', '--note=my key'])

        self.assertEqual(result.exit_code, 0)
        self.assert_called_with('SoftLayer_Security_Ssh_Key', 'editObject',
                                args=({'notes': 'my key',
                                       'label': 'key1'},),
                                identifier=1234)

    def test_edit_key_fail(self):
        fixture = self.set_mock('SoftLayer_Security_Ssh_Key', 'editObject')
        fixture.return_value = False

        result = self.run_command(['sshkey', 'edit', '1234',
                                   '--label=key1', '--note=my key'])

        self.assertEqual(result.exit_code, 2)

    def test_list_keys(self):
        result = self.run_command(['sshkey', 'list'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output),
                         [{'notes': '-',
                           'fingerprint': None,
                           'id': '100',
                           'label': 'Test 1'},
                          {'notes': 'my key',
                           'fingerprint': None,
                           'id': '101',
                           'label': 'Test 2'}])

    def test_print_key(self):
        result = self.run_command(['sshkey', 'print', '1234'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output),
                         {'id': 1234, 'label': 'label', 'notes': 'notes'})

    def test_print_key_file(self):
        with tempfile.NamedTemporaryFile() as sshkey_file:
            service = self.client['Security_Ssh_Key']
            mock_key = service.getObject()['key']
            result = self.run_command(['sshkey', 'print', '1234',
                                       '--out-file=%s' % sshkey_file.name])

            self.assertEqual(result.exit_code, 0)
            self.assertEqual(mock_key, sshkey_file.read().decode("utf-8"))
