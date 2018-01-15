"""
    SoftLayer.sshkey
    ~~~~~~~~~~~~~~~~
    SSH Key Manager/helpers

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer import utils


class SshKeyManager(utils.IdentifierMixin, object):
    """Manages account SSH keys in SoftLayer.

    See product information here:
    https://knowledgelayer.softlayer.com/procedure/ssh-keys

    :param SoftLayer.API.BaseClient client: the client instance
    """

    def __init__(self, client):
        self.client = client
        self.sshkey = client['Security_Ssh_Key']
        self.resolvers = [self._get_ids_from_label]

    def add_key(self, key, label, notes=None):
        """Adds a new SSH key to the account.

        :param string key: The SSH key to add
        :param string label: The label for the key
        :param string notes: Additional notes for the key
        :returns: A dictionary of the new key's information.
        """
        order = {
            'key': key,
            'label': label,
            'notes': notes,
        }

        return self.sshkey.createObject(order)

    def delete_key(self, key_id):
        """Permanently deletes an SSH key from the account.

        :param int key_id: The ID of the key to delete

        """
        return self.sshkey.deleteObject(id=key_id)

    def edit_key(self, key_id, label=None, notes=None):
        """Edits information about an SSH key.

        :param int key_id: The ID of the key to edit
        :param string label: The new label for the key
        :param string notes: Notes to set or change on the key
        :returns: A Boolean indicating success or failure
        """
        data = {}

        if label:
            data['label'] = label

        if notes:
            data['notes'] = notes

        return self.sshkey.editObject(data, id=key_id)

    def get_key(self, key_id):
        """Returns full information about a single SSH key.

        :param int key_id: The ID of the key to retrieve
        :returns: A dictionary of information about the key
        """
        return self.sshkey.getObject(id=key_id)

    def list_keys(self, label=None):
        """Lists all SSH keys on the account.

        :param string label: Filter list based on SSH key label
        :returns: A list of dictionaries with information about each key
        """
        _filter = utils.NestedDict({})
        if label:
            _filter['sshKeys']['label'] = utils.query_filter(label)

        return self.client['Account'].getSshKeys(filter=_filter.to_dict())

    def _get_ids_from_label(self, label):
        """Return sshkey IDs which match the given label."""
        keys = self.list_keys()
        results = []
        for key in keys:
            if key['label'] == label:
                results.append(key['id'])
        return results
