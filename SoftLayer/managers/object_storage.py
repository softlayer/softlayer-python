"""
    SoftLayer.object_storage
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Object Storage Manager/helpers

    :license: MIT, see LICENSE for more details.
"""

LIST_ACCOUNTS_MASK = '''mask[
    id,username,notes,vendorName,serviceResource
]'''

ENDPOINT_MASK = '''mask(SoftLayer_Network_Storage_Hub_Swift)[
    id,storageNodes[id,backendIpAddress,frontendIpAddress,datacenter]
]'''


class ObjectStorageManager(object):
    """Manager for SoftLayer Object Storage accounts.

    See product information here: http://www.softlayer.com/object-storage

    :param SoftLayer.API.BaseClient client: the client instance

    """

    def __init__(self, client):
        self.client = client

    def list_accounts(self):
        """Lists your object storage accounts."""
        return self.client.call('Account', 'getHubNetworkStorage',
                                mask=LIST_ACCOUNTS_MASK)

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
