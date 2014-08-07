"""
    SoftLayer.tests.managers.sshkey_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

import SoftLayer
from SoftLayer import testing


class SshKeyTests(testing.TestCase):

    def set_up(self):
        self.client = testing.FixtureClient()
        self.sshkey = SoftLayer.SshKeyManager(self.client)

    def test_add_key(self):
        key = 'pretend this is a public SSH key'
        label = 'Test label'
        notes = 'My notes'

        data = {
            'key': key,
            'label': label,
            'notes': notes,
        }
        mcall = mock.call(data)
        service = self.client['Security_Ssh_Key']

        self.sshkey.add_key(key=key, label=label, notes=notes)
        service.createObject.assert_has_calls(mcall)

    def test_delete_key(self):
        id = 1234
        mcall = mock.call(id=id)
        service = self.client['Security_Ssh_Key']

        self.sshkey.delete_key(id)
        service.deleteObject.assert_has_calls(mcall)

    def test_edit_key(self):
        id = 1234
        label = 'Test label'
        notes = 'My notes'

        data = {
            'label': label,
            'notes': notes,
        }
        mcall = mock.call(data, id=id)
        service = self.client['Security_Ssh_Key']

        self.sshkey.edit_key(id, label=label, notes=notes)
        service.editObject.assert_has_calls(mcall)

    def test_get_key(self):
        id = 1234
        mcall = mock.call(id=id)
        service = self.client['Security_Ssh_Key']

        self.sshkey.get_key(id)
        service.getObject.assert_has_calls(mcall)

    def test_list_keys(self):
        service = self.client['Account']
        self.sshkey.list_keys(label='some label')
        service.getSshKeys.assert_called_with(
            filter={'sshKeys': {'label': {'operation': '_= some label'}}})

    def test_resolve_ids_label(self):
        _id = self.sshkey._get_ids_from_label('Test 1')
        self.assertEqual(_id, ['100'])

        _id = self.sshkey._get_ids_from_label('nope')
        self.assertEqual(_id, [])
