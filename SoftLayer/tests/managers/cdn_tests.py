"""
    SoftLayer.tests.managers.cdn_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.managers.cdn import (CDNManager, MAX_URLS_PER_LOAD,
                                    MAX_URLS_PER_PURGE)
from SoftLayer.tests import TestCase, FixtureClient
from SoftLayer.tests.fixtures import Account
from mock import call
from math import ceil


class CDNTests(TestCase):

    def set_up(self):
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

    def test_add_origin(self):
        account_id = 12345
        media_type = 'http'
        origin_url = 'http://localhost/',
        cname = 'self.local'
        secure = False

        self.cdn_client.add_origin(account_id, media_type,
                                   origin_url, cname, secure)

        service = self.client['Network_ContentDelivery_Account']
        service.createOriginPullMapping.assert_called_once_with({
            'mediaType': media_type,
            'originUrl': origin_url,
            'cname': cname,
            'isSecureContent': secure},
            id=account_id)

    def test_remove_origin(self):
        account_id = 12345
        id = 12345
        mcall = call(account_id, id=id)
        service = self.client['Network_ContentDelivery_Account']

        self.cdn_client.remove_origin(account_id, id)
        service.deleteOriginPullRule.assert_has_calls(mcall)

    def test_load_content(self):
        account_id = 12345
        urls = ['http://a/img/0x001.png',
                'http://b/img/0x002.png',
                'http://c/img/0x004.png',
                'http://d/img/0x008.png',
                'http://e/img/0x010.png',
                'http://e/img/0x020.png']

        self.cdn_client.load_content(account_id, urls)
        service = self.client['Network_ContentDelivery_Account']
        self.assertEqual(service.loadContent.call_count,
                         ceil(len(urls) / float(MAX_URLS_PER_LOAD)))

    def test_load_content_single(self):
        account_id = 12345
        url = 'http://geocities.com/Area51/Meteor/12345/under_construction.gif'
        self.cdn_client.load_content(account_id, url)
        service = self.client['Network_ContentDelivery_Account']
        service.loadContent.assert_called_once_with([url], id=account_id)

    def test_load_content_failure(self):
        account_id = 12345
        urls = ['http://z/img/0x004.png',
                'http://y/img/0x002.png',
                'http://x/img/0x001.png']

        service = self.client['Network_ContentDelivery_Account']
        service.loadContent.return_value = False

        self.cdn_client.load_content(account_id, urls)
        self.assertEqual(service.loadContent.call_count,
                         ceil(len(urls) / float(MAX_URLS_PER_LOAD)))

    def test_purge_content(self):
        account_id = 12345
        urls = ['http://z/img/0x020.png',
                'http://y/img/0x010.png',
                'http://x/img/0x008.png',
                'http://w/img/0x004.png',
                'http://v/img/0x002.png',
                'http://u/img/0x001.png']

        self.cdn_client.purge_content(account_id, urls)
        service = self.client['Network_ContentDelivery_Account']
        self.assertEqual(service.purgeContent.call_count,
                         ceil(len(urls) / float(MAX_URLS_PER_PURGE)))

    def test_purge_content_failure(self):
        account_id = 12345
        urls = ['http://z/img/0x004.png',
                'http://y/img/0x002.png',
                'http://x/img/0x001.png']

        service = self.client['Network_ContentDelivery_Account']
        service.purgeContent.return_value = False

        self.cdn_client.purge_content(account_id, urls)
        self.assertEqual(service.purgeContent.call_count,
                         ceil(len(urls) / float(MAX_URLS_PER_PURGE)))

    def test_purge_content_single(self):
        account_id = 12345
        url = 'http://geocities.com/Area51/Meteor/12345/under_construction.gif'
        service = self.client['Network_ContentDelivery_Account']

        self.cdn_client.purge_content(account_id, url)
        service.purgeContent.assert_called_once_with([url], id=account_id)
