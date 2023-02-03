"""
    SoftLayer.search
    ~~~~~~~~~~~~~~~~~~
    Search Manager

    :license: MIT, see LICENSE for more details.
"""


class SearchManager(object):
    """Manager to help searcha via the SoftLayer API.

    :param SoftLayer.API.BaseClient client: the client instance
    """

    def __init__(self, client):
        self.client = client
        self.search_manager = client['SoftLayer_Search']

    def get_object_types(self):
        """returns a collection of SoftLayer_Container_Search_ObjectType containers.

        """
        return self.search_manager.getObjectTypes()

    def search(self, search_string):
        """allows for searching for SoftLayer resources by simple phrase.

        """
        return self.search_manager.search(search_string)

    def advanced(self, search_string):
        """allows for searching for SoftLayer resources by simple phrase.

        """
        return self.search_manager.advancedSearch(search_string)
