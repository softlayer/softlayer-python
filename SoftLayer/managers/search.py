"""
    SoftLayer.search
    ~~~~~~~~~~~~~
    Search Manager/helpers
    SoftLayer/managers/search.py

    :copyright: (c) 2014, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""

TYPE_DEFAULT_MASKS = {
    'SoftLayer_Hardware': [
        'id',
        'fullyQualifiedDomainName'
    ],
    'SoftLayer_Virtual_Guest': [
        'id',
        'fullyQualifiedDomainName'
    ],
    'SoftLayer_Ticket': [
        'id',
        'title'
    ],
    'SoftLayer_Network_Subnet_IpAddress': [
        'id',
        'ipAddress'
    ],
    'SoftLayer_Network_Vlan': [
        'id',
        'primaryRouter.hostname',
        'vlanNumber'
    ],
    'SoftLayer_Network_Application_Delivery_Controller': [
        'id',
        'name'
    ],
    'SoftLayer_Network_Vlan_Firewall': [
        'id',
        'fullyQualifiedDomainName'
    ]
}


class SearchManager(object):

    """ Manage Search """
    def __init__(self, client):
        self.client = client
        self.search_client = client['Search']

    def search(self, query, types=None, **kwargs):
        """ Retrieve a list of objects from SoftLayer_Search::search results
        based on the query/search string provided.

        :param string query: Query to use for search against API objects.
        :param list types: List of types to specifically search for,
                            overriding the default of all data types.
        :param dict \*\*kwargs: response-level arguments (limit, offset, mask, etc.)
        :returns: A list of dictionaries of API object data.

        """
        if not types:
            # Need to raise error if no types given
            raise ValueError("Must provide a valid list of types to search on")

        # Add our object types to the query
        query = '%s _objectType:%s' % (query, ','.join(types))

        # Set our default masks for object types we are using
        if 'mask' not in kwargs:
            type_masks = []

            for t in types:
                if t in TYPE_DEFAULT_MASKS.keys():
                    type_masks.append("resource(%s)[%s]" % (t, ','.join(TYPE_DEFAULT_MASKS.get(t))))

            # Set the default mask
            kwargs['mask'] = 'mask[%s]' % ','.join(type_masks)

        results = self.search_client.search(query, **kwargs)

        return results

    def get_search_types(self, **kwargs):
        """ Retrieve a list of object types from SoftLayer_Search::getObjectTypes

        :returns: A list of strings of API object type names.

        """
        results = self.search_client.getObjectTypes(**kwargs)
        return [x.get('name') for x in results]
