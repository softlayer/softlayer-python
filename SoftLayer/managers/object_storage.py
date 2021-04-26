"""
    SoftLayer.object_storage
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Object Storage Manager/helpers

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.exceptions import SoftLayerError
from SoftLayer import utils

LIST_ACCOUNTS_MASK = '''mask[
    id,username,notes,vendorName,serviceResource
]'''

ENDPOINT_MASK = '''mask(SoftLayer_Network_Storage_Hub_Swift)[
    id,storageNodes[id,backendIpAddress,frontendIpAddress,datacenter]
]'''


class ObjectStorageManager(utils.IdentifierMixin, object):
    """Manager for SoftLayer Object Storage accounts.

    See product information here: https://www.ibm.com/cloud/object-storage

    :param SoftLayer.API.BaseClient client: the client instance

    """

    def __init__(self, client):
        self.client = client
        self.resolvers = [self._get_id_from_username]

    def list_accounts(self, object_mask=None, object_filter=None, limit=10):
        """Lists your object storage accounts."""
        object_mask = object_mask if object_mask else LIST_ACCOUNTS_MASK
        return self.client.call('Account',
                                'getHubNetworkStorage',
                                mask=object_mask,
                                filter=object_filter,
                                limit=limit)

    def list_endpoints(self):
        """Lists the known object storage endpoints."""
        _filter = {
            'hubNetworkStorage': {'vendorName': {'operation': 'Swift'}},
        }
        endpoints = []
        network_storage = self.client.call('Account',
                                           'getHubNetworkStorage',
                                           mask=ENDPOINT_MASK,
                                           limit=1,
                                           filter=_filter)
        if network_storage:
            for node in network_storage['storageNodes']:
                endpoints.append({
                    'datacenter': node['datacenter'],
                    'public': node['frontendIpAddress'],
                    'private': node['backendIpAddress'],
                })

        return endpoints

    def create_credential(self, identifier):
        """Create object storage credential.

        :param int identifier: The object storage account identifier.

        """

        return self.client.call('SoftLayer_Network_Storage_Hub_Cleversafe_Account', 'credentialCreate',
                                id=identifier)

    def delete_credential(self, identifier, credential_id=None):
        """Delete the object storage credential.

        :param int id: The object storage account identifier.
        :param int credential_id: The credential id to be deleted.

        """
        credential = {
            'id': credential_id
        }

        return self.client.call('SoftLayer_Network_Storage_Hub_Cleversafe_Account', 'credentialDelete',
                                credential, id=identifier)

    def limit_credential(self, identifier):
        """Limit object storage credentials.

        :param int identifier: The object storage account identifier.

        """

        return self.client.call('SoftLayer_Network_Storage_Hub_Cleversafe_Account', 'getCredentialLimit',
                                id=identifier)

    def list_credential(self, identifier):
        """List the object storage credentials.

        :param int identifier: The object storage account identifier.

        """

        return self.client.call('SoftLayer_Network_Storage_Hub_Cleversafe_Account', 'getCredentials',
                                id=identifier)

    def _get_id_from_username(self, username):
        """Looks up a username's id

        :param string username: Username to lookup
        :returns: The id that matches username.
        """
        _mask = "mask[id,username]"
        _filter = {'hubNetworkStorage': {'username': utils.query_filter(username)}}
        account = self.list_accounts(_mask, _filter)
        if len(account) == 1:
            return [account[0]['id']]
        elif len(account) > 1:
            raise SoftLayerError("Multiple object storage accounts found with the name: {}".format(username))
        else:
            raise SoftLayerError("Unable to find object storage account id for: {}".format(username))
