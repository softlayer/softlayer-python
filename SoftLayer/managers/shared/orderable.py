"""
    SoftLayer.managers.orderable
    ~~~~~~~~~~~~~~~~~~
    Code that can be inherited by managers in SoftLayer.managers to deal
    with ordering specific logic

    :license: MIT, see LICENSE for more details.
"""


class Orderable(object):
    """ Abstracts ordering specific logic
    """
    def get_packages_by_type(self, package_types, mask):
        """ Return all packages of a given type

        :param list package_types: list of package types (strings)
        :param string mask: Properties of the package objects to be returned

        :returns: A list of product packages that matched the package type
        """
        package_client = self._get_package_service()

        _filter = {
            'type': {
                'keyName': {
                    'operation': 'in',
                    'options': [
                        {'name': 'data',
                         'value': package_types}
                    ],
                },
            },
        }

        return package_client.getAllObjects(mask=mask, filter=_filter)

    def get_package_id_for_package_type(self, package_type):
        """ Return the ID for a given package type
        If multiple packages match the type provided, the last one is returned

        :param string package_type: Package type to be used for the search

        :returns: An integer value or None if no package found
        """
        packages = self.get_packages_by_type([package_type],
                                             'id,type[keyName]')
        package_id = None
        for package in packages:
            if 'type' in package \
                    and package['type']['keyName'] == package_type:
                package_id = package['id']

        return package_id

    def _get_package_service(self):
        """ Return the package service to make our application calls

        :returns: A SoftLayer Service
        :raises: NotImplementedError when managers do not override this
        """
        raise NotImplementedError("Each manager must supply its own client")
