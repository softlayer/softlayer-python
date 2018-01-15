"""
    SoftLayer.ordering
    ~~~~~~~~~~~~~~~~~~
    Ordering Manager

    :license: MIT, see LICENSE for more details.
"""
# pylint: disable=no-self-use

from SoftLayer import exceptions

CATEGORY_MASK = '''id,
                   isRequired,
                   itemCategory[id, name, categoryCode]
                '''

ITEM_MASK = '''id, keyName, description, itemCategory, categories'''

PACKAGE_MASK = '''id, name, keyName, isActive, type'''

PRESET_MASK = '''id, name, keyName, description'''


class OrderingManager(object):
    """Manager to help ordering via the SoftLayer API.

    :param SoftLayer.API.BaseClient client: the client instance
    """

    def __init__(self, client):
        self.client = client
        self.package_svc = client['Product_Package']
        self.order_svc = client['Product_Order']
        self.billing_svc = client['Billing_Order']

    def get_packages_of_type(self, package_types, mask=None):
        """Get packages that match a certain type.

        Each ordering package has a type, so return all packages that match
        the types we are looking for

        :param list package_types: List of strings representing the package
                                   type keynames we are interested in.
        :param string mask: Mask to specify the properties we want to retrieve
        """

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

        packages = self.package_svc.getAllObjects(mask=mask, filter=_filter)
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

        :param packages: Dictionary of packages, isActive key must be present
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

        :param string package_type: representing the package type key name we are interested in
        """
        packages = self.get_packages_of_type([package_type], mask)
        if len(packages) == 0:
            return None
        else:
            return packages.pop()

    def get_package_id_by_type(self, package_type):
        """Return the package ID of a Product Package with a given type.

        :param string package_type: representing the package type key name we are interested in
        :raises ValueError: when no package of the given type is found
        """

        mask = "mask[id, name, description, isActive, type[keyName]]"
        package = self.get_package_by_type(package_type, mask)
        if package:
            return package['id']
        else:
            raise ValueError("No package found for type: " + package_type)

    def get_quotes(self):
        """Retrieve a list of quotes.

        :returns: a list of SoftLayer_Billing_Order_Quote
        """

        quotes = self.client['Account'].getActiveQuotes()
        return quotes

    def get_quote_details(self, quote_id):
        """Retrieve quote details.

        :param quote_id: ID number of target quote
        """

        quote = self.client['Billing_Order_Quote'].getObject(id=quote_id)
        return quote

    def get_order_container(self, quote_id):
        """Generate an order container from a quote object.

        :param quote_id: ID number of target quote
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
            raise ValueError("You must specify extra for each server in the quote")

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

        container = self.generate_order_template(quote_id, extra, quantity=quantity)
        return self.order_svc.verifyOrder(container)

    def order_quote(self, quote_id, extra, quantity=1):
        """Places an order using a quote

        :param int quote_id: ID for the target quote
        :param list hostnames: hostnames of the servers
        :param string domain: domain of the new server
        :param int quantity: Quantity to override default
        """

        container = self.generate_order_template(quote_id, extra, quantity=quantity)
        return self.order_svc.placeOrder(container)

    def get_package_by_key(self, package_keyname, mask=None):
        """Get a single package with a given key.

        If no packages are found, returns None

        :param package_keyname: string representing the package key name we are interested in.
        :param string mask: Mask to specify the properties we want to retrieve
        """
        _filter = {'keyName': {'operation': package_keyname}}

        packages = self.package_svc.getAllObjects(mask=mask, filter=_filter)
        if len(packages) == 0:
            raise exceptions.SoftLayerError("Package {} does not exist".format(package_keyname))

        return packages.pop()

    def list_categories(self, package_keyname, **kwargs):
        """List the categories for the given package.

        :param str package_keyname: The package for which to get the categories.
        :returns: List of categories associated with the package
        """
        get_kwargs = {}
        get_kwargs['mask'] = kwargs.get('mask', CATEGORY_MASK)

        if 'filter' in kwargs:
            get_kwargs['filter'] = kwargs['filter']

        package = self.get_package_by_key(package_keyname, mask='id')
        categories = self.package_svc.getConfiguration(id=package['id'], **get_kwargs)
        return categories

    def list_items(self, package_keyname, **kwargs):
        """List the items for the given package.

        :param str package_keyname: The package for which to get the items.
        :returns: List of items in the package

        """
        get_kwargs = {}
        get_kwargs['mask'] = kwargs.get('mask', ITEM_MASK)

        if 'filter' in kwargs:
            get_kwargs['filter'] = kwargs['filter']

        package = self.get_package_by_key(package_keyname, mask='id')
        items = self.package_svc.getItems(id=package['id'], **get_kwargs)
        return items

    def list_packages(self, **kwargs):
        """List active packages.

        :returns: List of active packages.

        """
        get_kwargs = {}
        get_kwargs['mask'] = kwargs.get('mask', PACKAGE_MASK)

        if 'filter' in kwargs:
            get_kwargs['filter'] = kwargs['filter']

        packages = self.package_svc.getAllObjects(**get_kwargs)

        return [package for package in packages if package['isActive']]

    def list_presets(self, package_keyname, **kwargs):
        """Gets active presets for the given package.

        :param str package_keyname: The package for which to get presets
        :returns: A list of package presets that can be used for ordering

        """
        get_kwargs = {}
        get_kwargs['mask'] = kwargs.get('mask', PRESET_MASK)

        if 'filter' in kwargs:
            get_kwargs['filter'] = kwargs['filter']

        package = self.get_package_by_key(package_keyname, mask='id')
        acc_presets = self.package_svc.getAccountRestrictedActivePresets(id=package['id'], **get_kwargs)
        active_presets = self.package_svc.getActivePresets(id=package['id'], **get_kwargs)
        return active_presets + acc_presets

    def get_preset_by_key(self, package_keyname, preset_keyname, mask=None):
        """Gets a single preset with the given key."""
        preset_operation = '_= %s' % preset_keyname
        _filter = {'activePresets': {'keyName': {'operation': preset_operation}}}

        presets = self.list_presets(package_keyname, mask=mask, filter=_filter)

        if len(presets) == 0:
            raise exceptions.SoftLayerError(
                "Preset {} does not exist in package {}".format(preset_keyname,
                                                                package_keyname))

        return presets[0]

    def get_price_id_list(self, package_keyname, item_keynames):
        """Converts a list of item keynames to a list of price IDs.

        This function is used to convert a list of item keynames into
        a list of price IDs that are used in the Product_Order verifyOrder()
        and placeOrder() functions.

        :param str package_keyname: The package associated with the prices
        :param list item_keynames: A list of item keyname strings
        :returns: A list of price IDs associated with the given item
                  keynames in the given package

        """
        mask = 'id, keyName, prices'
        items = self.list_items(package_keyname, mask=mask)

        prices = []
        for item_keyname in item_keynames:
            try:
                # Need to find the item in the package that has a matching
                # keyName with the current item we are searching for
                matching_item = [i for i in items
                                 if i['keyName'] == item_keyname][0]
            except IndexError:
                raise exceptions.SoftLayerError(
                    "Item {} does not exist for package {}".format(item_keyname,
                                                                   package_keyname))

            # we want to get the price ID that has no location attached to it,
            # because that is the most generic price. verifyOrder/placeOrder
            # can take that ID and create the proper price for us in the location
            # in which the order is made
            price_id = [p['id'] for p in matching_item['prices']
                        if p['locationGroupId'] == ''][0]
            prices.append(price_id)

        return prices

    def verify_order(self, package_keyname, location, item_keynames, complex_type=None,
                     hourly=True, preset_keyname=None, extras=None, quantity=1):
        """Verifies an order with the given package and prices.

        This function takes in parameters needed for an order and verifies the order
        to ensure the given items are compatible with the given package.

        :param str package_keyname: The keyname for the package being ordered
        :param str location: The datacenter location string for ordering (Ex: DALLAS13)
        :param list item_keynames: The list of item keyname strings to order. To see list of
                                   possible keynames for a package, use list_items()
                                   (or `slcli order item-list`)
        :param str complex_type: The complex type to send with the order. Typically begins
                                 with `SoftLayer_Container_Product_Order_`.
        :param bool hourly: If true, uses hourly billing, otherwise uses monthly billing
        :param string preset_keyname: If needed, specifies a preset to use for that package.
                                      To see a list of possible keynames for a package, use
                                      list_preset() (or `slcli order preset-list`)
        :param dict extras: The extra data for the order in dictionary format.
                            Example: A VSI order requires hostname and domain to be set, so
                            extras will look like the following:
                            'virtualGuests': [{'hostname': 'test', 'domain': 'softlayer.com'}]}
        :param int quantity: The number of resources to order

        """
        order = self.generate_order(package_keyname, location, item_keynames,
                                    complex_type=complex_type, hourly=hourly,
                                    preset_keyname=preset_keyname,
                                    extras=extras, quantity=quantity)
        return self.order_svc.verifyOrder(order)

    def place_order(self, package_keyname, location, item_keynames, complex_type=None,
                    hourly=True, preset_keyname=None, extras=None, quantity=1):
        """Places an order with the given package and prices.

        This function takes in parameters needed for an order and places the order.

        :param str package_keyname: The keyname for the package being ordered
        :param str location: The datacenter location string for ordering (Ex: DALLAS13)
        :param list item_keynames: The list of item keyname strings to order. To see list of
                                   possible keynames for a package, use list_items()
                                   (or `slcli order item-list`)
        :param str complex_type: The complex type to send with the order. Typically begins
                                 with `SoftLayer_Container_Product_Order_`.
        :param bool hourly: If true, uses hourly billing, otherwise uses monthly billing
        :param string preset_keyname: If needed, specifies a preset to use for that package.
                                      To see a list of possible keynames for a package, use
                                      list_preset() (or `slcli order preset-list`)
        :param dict extras: The extra data for the order in dictionary format.
                            Example: A VSI order requires hostname and domain to be set, so
                            extras will look like the following:
                            {'virtualGuests': [{'hostname': 'test', domain': 'softlayer.com'}]}
        :param int quantity: The number of resources to order

        """
        order = self.generate_order(package_keyname, location, item_keynames,
                                    complex_type=complex_type, hourly=hourly,
                                    preset_keyname=preset_keyname,
                                    extras=extras, quantity=quantity)
        return self.order_svc.placeOrder(order)

    def generate_order(self, package_keyname, location, item_keynames, complex_type=None,
                       hourly=True, preset_keyname=None, extras=None, quantity=1):
        """Generates an order with the given package and prices.

        This function takes in parameters needed for an order and generates an order
        dictionary. This dictionary can then be used in either verify or placeOrder().

        :param str package_keyname: The keyname for the package being ordered
        :param str location: The datacenter location string for ordering (Ex: DALLAS13)
        :param list item_keynames: The list of item keyname strings to order. To see list of
                                   possible keynames for a package, use list_items()
                                   (or `slcli order item-list`)
        :param str complex_type: The complex type to send with the order. Typically begins
                                 with `SoftLayer_Container_Product_Order_`.
        :param bool hourly: If true, uses hourly billing, otherwise uses monthly billing
        :param string preset_keyname: If needed, specifies a preset to use for that package.
                                      To see a list of possible keynames for a package, use
                                      list_preset() (or `slcli order preset-list`)
        :param dict extras: The extra data for the order in dictionary format.
                            Example: A VSI order requires hostname and domain to be set, so
                            extras will look like the following:
                            {'virtualGuests': [{'hostname': 'test', 'domain': 'softlayer.com'}]}
        :param int quantity: The number of resources to order

        """
        order = {}
        extras = extras or {}

        package = self.get_package_by_key(package_keyname, mask='id')

        # if there was extra data given for the order, add it to the order
        # example: VSIs require hostname and domain set on the order, so
        # extras will be {'virtualGuests': [{'hostname': 'test',
        #                                    'domain': 'softlayer.com'}]}
        order.update(extras)
        order['packageId'] = package['id']
        order['location'] = location
        order['quantity'] = quantity
        order['useHourlyPricing'] = hourly

        if preset_keyname:
            preset_id = self.get_preset_by_key(package_keyname, preset_keyname)['id']
            order['presetId'] = preset_id

        if not complex_type:
            raise exceptions.SoftLayerError("A complex type must be specified with the order")
        order['complexType'] = complex_type

        price_ids = self.get_price_id_list(package_keyname, item_keynames)
        order['prices'] = [{'id': price_id} for price_id in price_ids]
        return order

    def package_locations(self, package_keyname):
        """List datacenter locations for a package keyname

        :param str package_keyname: The package for which to get the items.
        :returns: List of locations a package is orderable in
        """
        mask = "mask[description, keyname, locations]"

        package = self.get_package_by_key(package_keyname, mask='id')

        regions = self.package_svc.getRegions(id=package['id'], mask=mask)
        return regions
