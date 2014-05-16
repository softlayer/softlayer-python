"""
    SoftLayer.tests.CLI.modules.cdn_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.tests import TestCase, FixtureClient
from SoftLayer.CLI.helpers import format_output
from SoftLayer.CLI.modules import cdn


class CdnTests(TestCase):
    def set_up(self):
        self.client = FixtureClient()

    def test_list_accounts(self):
        command = cdn.ListAccounts(client=self.client)

        output = command.execute({'--sortby': None})
        self.assertEqual([{'notes': None,
                           'created': '2012-06-25T14:05:28-07:00',
                           'type': 'ORIGIN_PULL',
                           'id': 1234,
                           'account_name': '1234a'},
                          {'notes': None,
                           'created': '2012-07-24T13:34:25-07:00',
                           'type': 'POP_PULL',
                           'id': 1234,
                           'account_name': '1234a'}],
                         format_output(output, 'python'))

    def test_detail_account(self):
        command = cdn.DetailAccount(client=self.client)

        output = command.execute({'<account>': '1234'})
        self.assertEqual({'notes': None,
                          'created': '2012-06-25T14:05:28-07:00',
                          'type': 'ORIGIN_PULL',
                          'status': 'ACTIVE',
                          'id': 1234,
                          'account_name': '1234a'},
                         format_output(output, 'python'))

    def test_load_content(self):
        command = cdn.LoadContent(client=self.client)

        output = command.execute({'<account>': '1234',
                                  '<content_url>': ['http://example.com']})
        self.assertEqual(None, output)

    def test_purge_content(self):
        command = cdn.PurgeContent(client=self.client)

        output = command.execute({'<account>': '1234',
                                  '<content_url>': ['http://example.com']})
        self.assertEqual(None, output)

    def test_list_origins(self):
        command = cdn.ListOrigins(client=self.client)

        output = command.execute({'<account>': '1234'})
        self.assertEqual([
            {'media_type': 'FLASH',
             'origin_url': 'http://ams01.objectstorage.softlayer.net:80',
             'cname': None,
             'id': '12345'},
            {'media_type': 'FLASH',
             'origin_url': 'http://sng01.objectstorage.softlayer.net:80',
             'cname': None,
             'id': '12345'}], format_output(output, 'python'))

    def test_add_origin(self):
        command = cdn.AddOrigin(client=self.client)

        output = command.execute({'<account>': '1234',
                                  '<url>': 'http://example.com'})
        self.assertEqual(None, output)

    def test_remove_origin(self):
        command = cdn.RemoveOrigin(client=self.client)

        output = command.execute({'<account>': '1234',
                                  '<origin_id>': '12345'})
        self.assertEqual(None, output)
