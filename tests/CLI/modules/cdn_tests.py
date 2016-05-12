"""
    SoftLayer.tests.CLI.modules.cdn_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing

import json


class CdnTests(testing.TestCase):

    def test_list_accounts(self):
        result = self.run_command(['cdn', 'list'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{'notes': None,
                           'created': '2012-06-25T14:05:28-07:00',
                           'type': 'ORIGIN_PULL',
                           'id': 1234,
                           'account_name': '1234a'},
                          {'notes': None,
                           'created': '2012-07-24T13:34:25-07:00',
                           'type': 'POP_PULL',
                           'id': 1234,
                           'account_name': '1234a'}])

    def test_detail_account(self):
        result = self.run_command(['cdn', 'detail', '1245'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         {'notes': None,
                          'created': '2012-06-25T14:05:28-07:00',
                          'type': 'ORIGIN_PULL',
                          'status': 'ACTIVE',
                          'id': 1234,
                          'account_name': '1234a'})

    def test_load_content(self):
        result = self.run_command(['cdn', 'load', '1234',
                                   'http://example.com'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")

    def test_purge_content(self):
        result = self.run_command(['cdn', 'purge', '1234',
                                   'http://example.com'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")

    def test_list_origins(self):
        result = self.run_command(['cdn', 'origin-list', '1234'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), [
            {'media_type': 'FLASH',
             'origin_url': 'http://ams01.objectstorage.softlayer.net:80',
             'cname': None,
             'id': '12345'},
            {'media_type': 'FLASH',
             'origin_url': 'http://sng01.objectstorage.softlayer.net:80',
             'cname': None,
             'id': '12345'}])

    def test_add_origin(self):
        result = self.run_command(['cdn', 'origin-add', '1234',
                                   'http://example.com'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")

    def test_remove_origin(self):
        result = self.run_command(['cdn', 'origin-remove', '1234',
                                   'http://example.com'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")
