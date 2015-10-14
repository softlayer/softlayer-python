"""
    SoftLayer.tests.managers.sshkey_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import testing


class SshKeyTests(testing.TestCase):

    def set_up(self):
        self.sshkey = SoftLayer.SshKeyManager(self.client)

    def test_add_key(self):
        self.sshkey.add_key(key='pretend this is a public SSH key',
                            label='Test label',
                            notes='My notes')

        args = ({
            'key':  'pretend this is a public SSH key',
            'label': 'Test label',
            'notes': 'My notes',
        },)
        self.assert_called_with('SoftLayer_Security_Ssh_Key', 'createObject',
                                args=args)

    def test_delete_key(self):
        self.sshkey.delete_key(1234)

        self.assert_called_with('SoftLayer_Security_Ssh_Key', 'deleteObject',
                                identifier=1234)

    def test_edit_key(self):
        self.sshkey.edit_key(1234, label='Test label', notes='My notes')

        args = ({
            'label': 'Test label',
            'notes': 'My notes',
        },)
        self.assert_called_with('SoftLayer_Security_Ssh_Key', 'editObject',
                                identifier=1234,
                                args=args)

    def test_get_key(self):
        self.sshkey.get_key(1234)

        self.assert_called_with('SoftLayer_Security_Ssh_Key', 'getObject',
                                identifier=1234)

    def test_list_keys(self):
        self.sshkey.list_keys(label='some label')

        _filter = {'sshKeys': {'label': {'operation': '_= some label'}}}
        self.assert_called_with('SoftLayer_Account', 'getSshKeys',
                                filter=_filter)

    def test_resolve_ids_label(self):
        _id = self.sshkey._get_ids_from_label('Test 1')
        self.assertEqual(_id, ['100'])

        _id = self.sshkey._get_ids_from_label('nope')
        self.assertEqual(_id, [])
