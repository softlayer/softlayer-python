"""
    SoftLayer.search
    ~~~~~~~~~~~~~~~~
    Search Manager

    :license: MIT, see LICENSE for more details.
"""


class SearchManager(object):
    """Manager to help search via the SoftLayer API.

    :param SoftLayer.API.BaseClient client: the client instance
    """

    def __init__(self, client):
        self.client = client
        self.search_manager = client['SoftLayer_Search']

    def get_object_types(self):
        """returns a collection of SoftLayer_Container_Search_ObjectType containers."""
        return self.search_manager.getObjectTypes()

    def search(self, search_string):
        """allows for searching for SoftLayer resources by simple phrase."""
        return self.search_manager.search(search_string)

    def advanced(self, search_string):
        """Uses the SoftLayer_Search::advancedSearch API. Allows for more complicated search phrases."""
        return self.search_manager.advancedSearch(search_string)

    def search_instances(self, search_string, mask=None, **kwargs):
        """Lists VSIs based in the search_string.

        Also takes in a few search terms as \\*\\*kwargs. such as hostname, datacenter, domain and tags
        """

        # This forces the Search API to do a fuzzy search on our term, kinda. Not sure why the ** are
        # Required but it will do an exact search without them.
        if search_string:
            search_string = f"*{search_string}*"
        search_string = f"_objectType:SoftLayer_Virtual_Guest {search_string}"
        if kwargs.get('hostname'):
            search_string = f"{search_string} hostname: *{kwargs.get('hostname')}*"
        if kwargs.get('domain'):
            search_string = f"{search_string} domain: *{kwargs.get('domain')}*"
        if kwargs.get('datacenter'):
            search_string = f"{search_string} datacenter.longName: *{kwargs.get('datacenter')}*"
        if kwargs.get('tags'):
            tags = " ".join(kwargs.get("tags", []))
            search_string = f"{search_string} internalTagReferences.tag.name: {tags}"
        result = self.search_manager.advancedSearch(search_string, mask=mask)
        guests = []
        for resource in result:
            guests.append(resource.get('resource'))

        return guests

    def search_hadrware_instances(self, search_string, mask=None, **kwargs):
        """Lists hardwares based in the search_string.

        Also takes in a few search terms as \\*\\*kwargs. such as hostname, datacenter, domain and tags
        """

        # This forces the Search API to do a fuzzy search on our term, kinda. Not sure why the ** are
        # Required but it will do an exact search without them.
        if search_string:
            search_string = f"*{search_string}*"
        search_string = f"_objectType:SoftLayer_Hardware {search_string}"
        if kwargs.get('hostname'):
            search_string = f"{search_string} hostname: *{kwargs.get('hostname')}*"
        if kwargs.get('domain'):
            search_string = f"{search_string} domain: *{kwargs.get('domain')}*"
        if kwargs.get('cpu'):
            search_string = f"{search_string} cpu: *{kwargs.get('cpu')}*"
        if kwargs.get('network'):
            search_string = f"{search_string} network: *{kwargs.get('network')}*"
        if kwargs.get('memory'):
            search_string = f"{search_string} memory: *{kwargs.get('memory')}*"
        if kwargs.get('datacenter'):
            search_string = f"{search_string} datacenter.longName: *{kwargs.get('datacenter')}*"
        if kwargs.get('tags'):
            tags = " ".join(kwargs.get("tags", []))
            search_string = f"{search_string} internalTagReferences.tag.name: {tags}"
        result = self.search_manager.advancedSearch(search_string, mask=mask)
        servers = []
        for resource in result:
            servers.append(resource.get('resource'))

        return servers
