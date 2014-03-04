"""
    SoftLayer.tests.managers.cdn_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.managers.cdn import CDNManager
from SoftLayer.tests import unittest, FixtureClient
from SoftLayer.tests.fixtures import Account
from mock import call


class CDNTests(unittest.TestCase):

    def setUp(self):
        self.client = FixtureClient()
        self.cdn_client = CDNManager(self.client)

    def test_list_accounts(self):
        accounts = self.cdn_client.list_accounts()
        self.assertEqual(accounts, Account.getCdnAccounts)

    def test_get_account(self):
        account = self.cdn_client.get_account(12345)
        account_fixtures = self.client['Network_ContentDelivery_Account'].\
            getObject(id=12345)
        self.assertEqual(account, account_fixtures)

    def test_get_origins(self):
        origins = self.cdn_client.get_origins(12345)
        origins_fixture = self.client['Network_ContentDelivery_Account'].\
            getOriginPullMappingInformation(id=12345)
        self.assertEqual(origins, origins_fixture)

    def test_remove_origin(self):
        account_id = 12345
        id = 12345
        mcall = call(account_id, id=id)
        service = self.client['Network_ContentDelivery_Account']

        self.cdn_client.remove_origin(account_id, id)
        service.deleteOriginPullRule.assert_has_calls(mcall)
