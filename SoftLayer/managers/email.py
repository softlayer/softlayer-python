"""
    SoftLayer.account
    ~~~~~~~~~~~~~~~~~~~~~~~
    Account manager

    :license: MIT, see License for more details.
"""

from SoftLayer import utils


# Invalid names are ignored due to long method names and short argument names
# pylint: disable=invalid-name, no-self-use


class EmailManager(utils.IdentifierMixin, object):
    """Common functions for getting information from the Account service

    :param SoftLayer.API.BaseClient client: the client instance
    """

    def __init__(self, client):
        self.client = client

    def get_AccountOverview(self, identifier):
        """Gets all the Network Message Delivery Account Overview

        :returns: Network Message Delivery Account overview
        """
        return self.client.call('SoftLayer_Network_Message_Delivery_Email_Sendgrid',
                                'getAccountOverview', id=identifier)

    def get_statistics(self, identifier, selectedStatistics,
                       startDate, endDate, aggregatesOnly, days):
        """Gets statistics Network Message Delivery Account

        :returns: statistics Network Message Delivery Account
        """
        body = [selectedStatistics,
                startDate,
                endDate,
                aggregatesOnly,
                days
                ]

        return self.client.call('SoftLayer_Network_Message_Delivery_Email_Sendgrid',
                                'getStatistics', id=identifier, *body)
