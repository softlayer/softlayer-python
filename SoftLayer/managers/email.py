"""
    SoftLayer.email
    ~~~~~~~~~~~~~~~~~~~~~~~
    Email manager

    :license: MIT, see License for more details.
"""

from SoftLayer import utils


# Invalid names are ignored due to long method names and short argument names
# pylint: disable=invalid-name, no-self-use


class EmailManager(utils.IdentifierMixin, object):
    """Common functions for getting information from the email service

    :param SoftLayer.API.BaseClient client: the client instance
    """

    def __init__(self, client):
        self.client = client

    def get_account_overview(self, identifier):
        """Gets all the Network Message Delivery Account Overview

        :returns: Network Message Delivery Account overview
        """
        return self.client.call('SoftLayer_Network_Message_Delivery_Email_Sendgrid',
                                'getAccountOverview', id=identifier)

    def get_statistics(self, identifier, days=30):
        """gets statistics from email accounts

        :days: range number
        :returns: statistics Network Message Delivery Account
        """
        body = [["requests", "delivered", "opens", "clicks", "bounds"],
                True,
                True,
                True,
                days
                ]

        return self.client.call('SoftLayer_Network_Message_Delivery_Email_Sendgrid',
                                'getStatistics', id=identifier, *body)

    def get_instance(self, identifier):
        """Gets the Network_Message_Delivery_Email_Sendgrid instance

        :return: Network_Message_Delivery_Email_Sendgrid
        """

        _mask = """emailAddress,type,billingItem,vendor"""

        return self.client.call('SoftLayer_Network_Message_Delivery_Email_Sendgrid',
                                'getObject', id=identifier, mask=_mask)

    def editObject(self, identifier, username=None, password=None):
        """Edit email delivery account related details.

               :param int identifier: The ID of the email account
               :param string username: username of the email account.
               :param string email: email of the email account.
               :param string password: password of the email account to be updated to.
               """
        data = {}
        if username:
            data['username'] = username
        if password:
            data['password'] = password

        return self.client.call('SoftLayer_Network_Message_Delivery_Email_Sendgrid',
                                'editObject', data, id=identifier)

    def update_email(self, identifier, email):
        """Edit email address delivery account .

        :param int identifier: The ID of the email account
        :param string email: email of the email account.

        """
        return self.client.call('SoftLayer_Network_Message_Delivery_Email_Sendgrid',
                                'updateEmailAddress', email, id=identifier)
