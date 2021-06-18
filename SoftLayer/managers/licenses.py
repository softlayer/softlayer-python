"""
    SoftLayer.license
    ~~~~~~~~~~~~~~~
    License Manager
    :license: MIT, see LICENSE for more details.
"""


# pylint: disable=too-many-public-methods


class LicensesManager(object):
    """Manages account lincese."""

    def __init__(self, client):
        self.client = client

    def get_create_options(self):
        """Returns valid options for ordering Licenses.

        :param string datacenter: short name, like dal09
        """

        return self.client.call('SoftLayer_Product_Package', 'getItems',
                                id=301)
