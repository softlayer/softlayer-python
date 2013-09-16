"""
    SoftLayer.sshkey
    ~~~~~~~~~~~~~~~~
    SSH Key Manager/helpers

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.utils import IdentifierMixin


class SshKeyManager(IdentifierMixin, object):
    """
    Manages account SSH keys.

    :param SoftLayer.API.Client client: an API client instance
    """

    def __init__(self, client):
        #: A valid `SoftLayer.API.Client` object that will be used for all
        #: actions.
        self.client = client
        #: Reference to the SoftLayer_Security_Ssh_Key API object.
        self.sshkey = client['Security_Ssh_Key']
        #: A list of resolver functions. Used primarily by the CLI to provide
        #: a variety of methods for uniquely identifying an object such as
        #: label.
        self.resolvers = [self._get_ids_from_label]

    def add_key(self, key, label, notes=None):
        """ Adds a new SSH key to the account.

        :param string key: The SSH key to add
        :param string label: The label for the key
        :returns: A dictionary of the new key's information.
        """
        order = {
            'key': key,
            'label': label,
            'notes': notes,
        }

        return self.sshkey.createObject(order)

    def delete_key(self, id):
        """ Permanently deletes an SSH key from the account.

        :param int id: The ID of the key to delete

        """
        return self.sshkey.deleteObject(id=id)

    def edit_key(self, id, label=None, notes=None):
        """ Edits information about an SSH key.

        :param int id: The ID of the key to edit
        :param string label: The new label for the key
        :param string notes: Notes to set or change on the key
        :returns: A Boolean indicating success or failure
        """
        data = {}

        if label:
            data['label'] = label

        if notes:
            data['notes'] = notes

        return self.sshkey.editObject(data, id=id)

    def get_key(self, id):
        """ Returns full information about a single SSH key.

        :param int id: The ID of the key to retrieve
        :returns: A dictionary of information about the key
        """
        return self.sshkey.getObject(id=id)

    def list_keys(self):
        """ Lists all SSH keys on the account. """
        return self.client['Account'].getSshKeys()

    def _get_ids_from_label(self, label):
        keys = self.list_keys()
        results = []
        for key in keys:
            if key['label'] == label:
                results.append(key['id'])
        return results
