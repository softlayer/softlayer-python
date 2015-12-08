"""
    SoftLayer.object_storage
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Object Storage Manager/helpers

    :license: MIT, see LICENSE for more details.
"""

LIST_ACCOUNTS_MASK = '''mask(SoftLayer_Network_Storage_Hub_Swift)[
    id,username,notes
]'''

ENDPOINT_MASK = '''mask(SoftLayer_Network_Storage_Hub_Swift)[
    id,storageNodes[id,backendIpAddress,frontendIpAddress,datacenter]
]'''


class ObjectStorageManager(object):
    """Manager for Object Storage."""

    def __init__(self, client):
        self.client = client

    def list_accounts(self):
        """Lists your object storage accounts."""
        _filter = {
            'hubNetworkStorage': {'vendorName': {'operation': 'Swift'}},
        }
        return self.client.call('Account', 'getHubNetworkStorage',
                                mask=LIST_ACCOUNTS_MASK,
                                filter=_filter)

    def list_endpoints(self):
        """Lists the known object storage endpoints."""
        _filter = {
            'hubNetworkStorage': {'vendorName': {'operation': 'Swift'}},
        }
        endpoints = []
        for node in self.client.call('Account', 'getHubNetworkStorage',
                                     mask=ENDPOINT_MASK,
                                     limit=1,
                                     filter=_filter)['storageNodes']:
            endpoints.append({
                'datacenter': node['datacenter'],
                'public': node['frontendIpAddress'],
                'private': node['backendIpAddress'],
            })

        return endpoints
