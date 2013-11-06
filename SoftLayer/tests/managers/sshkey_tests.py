"""
    SoftLayer.tests.managers.sshkey_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import SshKeyManager
from SoftLayer.tests import unittest
from mock import MagicMock, call


class SshKeyTests(unittest.TestCase):

    def setUp(self):
        self.client = MagicMock()
        self.sshkey = SshKeyManager(self.client)

    def test_add_key(self):
        key = 'pretend this is a public SSH key'
        label = 'Test label'
        notes = 'My notes'

        data = {
            'key': key,
            'label': label,
            'notes': notes,
        }
        mcall = call(data)
        service = self.client['Security_Ssh_Key']

        self.sshkey.add_key(key=key, label=label, notes=notes)
        service.createObject.assert_has_calls(mcall)

    def test_delete_key(self):
        id = 1234
        mcall = call(id=id)
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
        mcall = call(data, id=id)
        service = self.client['Security_Ssh_Key']

        self.sshkey.edit_key(id, label=label, notes=notes)
        service.editObject.assert_has_calls(mcall)

    def test_get_key(self):
        id = 1234
        mcall = call(id=id)
        service = self.client['Security_Ssh_Key']

        self.sshkey.get_key(id)
        service.getObject.assert_has_calls(mcall)

    def test_list_keys(self):
        service = self.client['Account']
        mcall = call(filter={
            'sshKeys': {'label': {'operation': '_= some label'}}})
        self.sshkey.list_keys(label='some label')
        service.getSshKeys.assert_has_calls(mcall)

    def test_resolve_ids_label(self):
        service = self.client['Account']
        service.getSshKeys.return_value = [
            {
                'id': '100',
                'label': 'Test 1',
            },
            {
                'id': '101',
                'label': 'Test 2',
                'notes': 'Test notes'
            },
        ]

        _id = self.sshkey._get_ids_from_label('Test 1')
        self.assertEqual(_id, ['100'])

        _id = self.sshkey._get_ids_from_label('nope')
        self.assertEqual(_id, [])
