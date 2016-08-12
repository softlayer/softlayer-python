"""
    SoftLayer.tests.managers.cdn_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import math

from SoftLayer import fixtures
from SoftLayer.managers import cdn
from SoftLayer import testing


class CDNTests(testing.TestCase):

    def set_up(self):
        self.cdn_client = cdn.CDNManager(self.client)

    def test_list_accounts(self):
        accounts = self.cdn_client.list_accounts()
        self.assertEqual(accounts, fixtures.SoftLayer_Account.getCdnAccounts)

    def test_get_account(self):
        account = self.cdn_client.get_account(12345)
        self.assertEqual(
            account,
            fixtures.SoftLayer_Network_ContentDelivery_Account.getObject)

    def test_get_origins(self):
        origins = self.cdn_client.get_origins(12345)
        self.assertEqual(
            origins,
            fixtures.SoftLayer_Network_ContentDelivery_Account.
            getOriginPullMappingInformation)

    def test_add_origin(self):
        self.cdn_client.add_origin(12345,
                                   'http',
                                   'http://localhost/',
                                   'self.local',
                                   False)

        args = ({
            'mediaType': 'http',
            'originUrl': 'http://localhost/',
            'cname': 'self.local',
            'isSecureContent': False
        },)
        self.assert_called_with('SoftLayer_Network_ContentDelivery_Account',
                                'createOriginPullMapping',
                                args=args,
                                identifier=12345)

    def test_remove_origin(self):
        self.cdn_client.remove_origin(12345, 12345)
        self.assert_called_with('SoftLayer_Network_ContentDelivery_Account',
                                'deleteOriginPullRule',
                                args=(12345,),
                                identifier=12345)

    def test_load_content(self):
        urls = ['http://a/img/0x001.png',
                'http://b/img/0x002.png',
                'http://c/img/0x004.png',
                'http://d/img/0x008.png',
                'http://e/img/0x010.png',
                'http://e/img/0x020.png']

        self.cdn_client.load_content(12345, urls)
        calls = self.calls('SoftLayer_Network_ContentDelivery_Account',
                           'loadContent')
        self.assertEqual(len(calls),
                         math.ceil(len(urls) / float(cdn.MAX_URLS_PER_LOAD)))

    def test_load_content_single(self):
        url = 'http://geocities.com/Area51/Meteor/12345/under_construction.gif'
        self.cdn_client.load_content(12345, url)

        self.assert_called_with('SoftLayer_Network_ContentDelivery_Account',
                                'loadContent',
                                args=([url],),
                                identifier=12345)

    def test_load_content_failure(self):
        urls = ['http://z/img/0x004.png',
                'http://y/img/0x002.png',
                'http://x/img/0x001.png']

        service = self.client['SoftLayer_Network_ContentDelivery_Account']
        service.loadContent.return_value = False

        self.cdn_client.load_content(12345, urls)
        calls = self.calls('SoftLayer_Network_ContentDelivery_Account',
                           'loadContent')
        self.assertEqual(len(calls),
                         math.ceil(len(urls) / float(cdn.MAX_URLS_PER_LOAD)))

    def test_purge_content(self):
        urls = ['http://z/img/0x020.png',
                'http://y/img/0x010.png',
                'http://x/img/0x008.png',
                'http://w/img/0x004.png',
                'http://v/img/0x002.png',
                'http://u/img/0x001.png']

        self.cdn_client.purge_content(12345, urls)
        calls = self.calls('SoftLayer_Network_ContentDelivery_Account',
                           'purgeCache')
        self.assertEqual(len(calls),
                         math.ceil(len(urls) / float(cdn.MAX_URLS_PER_PURGE)))

    def test_purge_content_failure(self):
        urls = ['http://z/img/0x004.png',
                'http://y/img/0x002.png',
                'http://x/img/0x001.png']

        mock = self.set_mock('SoftLayer_Network_ContentDelivery_Account',
                             'purgeCache')
        mock.return_value = False

        self.cdn_client.purge_content(12345, urls)
        calls = self.calls('SoftLayer_Network_ContentDelivery_Account',
                           'purgeCache')
        self.assertEqual(len(calls),
                         math.ceil(len(urls) / float(cdn.MAX_URLS_PER_PURGE)))

    def test_purge_content_single(self):
        url = 'http://geocities.com/Area51/Meteor/12345/under_construction.gif'

        self.cdn_client.purge_content(12345, url)
        self.assert_called_with('SoftLayer_Network_ContentDelivery_Account',
                                'purgeCache',
                                args=([url],),
                                identifier=12345)
