"""
    SoftLayer.ordering
    ~~~~~~~~~~~~~~~~~~
    Ordering Manager

    :license: MIT, see LICENSE for more details.
"""


class OrderingManager(object):
    """Manages hardware devices.

    :param SoftLayer.API.Client client: an API client instance
    """

    def __init__(self, client):
        self.client = client

    def get_packages_of_type(self, package_types, mask=None):
        """Get packages that match a certain type.

        Each ordering package has a type, so return all packages that match
        the types we are looking for

        :param list package_types: List of strings representing the package
                                   type keynames we are interested in.
        :param string mask: Mask to specify the properties we want to retrieve
        """

        package_service = self.client['Product_Package']
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

        packages = package_service.getAllObjects(mask=mask, filter=_filter)
        packages = self.filter_outlet_packages(packages)
        return packages

    @staticmethod
    def filter_outlet_packages(packages):
        """Remove packages designated as OUTLET.

        Those type of packages must be handled in a different way,
        and they are not supported at the moment.

        :param packages: Dictionary of packages. Name and description keys
                         must be present in each of them.
        """

        non_outlet_packages = []

        for package in packages:
            if all(['OUTLET' not in package.get('description', '').upper(),
                    'OUTLET' not in package.get('name', '').upper()]):
                non_outlet_packages.append(package)

        return non_outlet_packages

    @staticmethod
    def get_only_active_packages(packages):
        """Return only active packages.

        If a package is active, it is eligible for ordering
        This will inspect the 'isActive' property on the provided packages

        :param packages Dictionary of packages, isActive key must be present
        """

        active_packages = []

        for package in packages:
            if package['isActive']:
                active_packages.append(package)

        return active_packages

    def get_package_by_type(self, package_type, mask=None):
        """Get a single package of a given type.

        Syntactic sugar to retrieve a single package of a given type.
        If multiple packages share the given type, this will return the first
        one returned by the API.
        If no packages are found, returns None

        :param package_type string representing the package type key name
                            we are interested in
        """
        packages = self.get_packages_of_type([package_type], mask)
        if len(packages) == 0:
            return None
        else:
            return packages.pop()

    def get_package_id_by_type(self, package_type):
        """Return the package ID of a Product Package with a given type.

        :param package_type string representing the package type key name
                            we are interested in
        :raises ValueError when no package of the given type is found
        """

        mask = "mask[id, name, description, isActive, type[keyName]]"
        package = self.get_package_by_type(package_type, mask)
        if package:
            return package['id']
        else:
            raise ValueError("No package found for type: " + package_type)

    def get_quotes(self):
        """Retrieve a list of quotes.

        :return a list of SoftLayer_Billing_Order_Quote
        """

        quotes = self.client['Account'].getActiveQuotes()
        return quotes

    def get_quote_details(self, quote_id):
        """Retrieve quote details.

        :param quote_id ID number of target quote
        """

        quote = self.client['Billing_Order_Quote'].getObject(id=quote_id)
        return quote

    def get_order_container(self, quote_id):
        """Generate an order container from a quote object.

        :param quote_id ID number of target quote
        """

        quote = self.client['Billing_Order_Quote']
        container = quote.getRecalculatedOrderContainer(id=quote_id)
        return container['orderContainers'][0]

    def generate_order_template(self, quote_id, extra, quantity=1):
        """Generate a complete order template.

        :param int quote_id: ID of target quote
        :param list extra: List of dictionaries that have extra details about
                           the order such as hostname or domain names for
                           virtual servers or hardware nodes
        :param int quantity: Number of ~things~ to order
        """

        container = self.get_order_container(quote_id)
        container['quantity'] = quantity

        # NOTE(kmcdonald): This will only work with virtualGuests and hardware.
        #                  There has to be a better way, since this is based on
        #                  an existing quote that supposedly knows about this
        #                  detail
        if container['packageId'] == 46:
            product_type = 'virtualGuests'
        else:
            product_type = 'hardware'

        if len(extra) != quantity:
            raise ValueError("You must specify extra for each server in the "
                             "quote")

        container[product_type] = []
        for extra_details in extra:
            container[product_type].append(extra_details)
        container['presetId'] = None
        return container

    def verify_quote(self, quote_id, extra, quantity=1):
        """Verifies that a quote order is valid.

        :param int quote_id: ID for the target quote
        :param list hostnames: hostnames of the servers
        :param string domain: domain of the new servers
        :param int quantity: Quantity to override default
        """

        container = self.generate_order_template(quote_id, extra,
                                                 quantity=quantity)
        return self.client['Product_Order'].verifyOrder(container)

    def order_quote(self, quote_id, extra, quantity=1):
        """Places an order using a quote

        :param int quote_id: ID for the target quote
        :param list hostnames: hostnames of the servers
        :param string domain: domain of the new server
        :param int quantity: Quantity to override default
        """

        container = self.generate_order_template(quote_id, extra,
                                                 quantity=quantity)
        return self.client['Product_Order'].placeOrder(container)
