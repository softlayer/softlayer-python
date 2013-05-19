"""
    SoftLayer.tests.API.metadata_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import SoftLayer

try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA
from mock import patch, MagicMock


class MetadataTests(unittest.TestCase):

    def setUp(self):
        self.metadata = SoftLayer.MetadataManager()
        self.make_request = MagicMock()
        self.metadata.make_request = self.make_request

    def test_no_param(self):
        self.make_request.return_value = '"dal01"'
        r = self.metadata.get('datacenter')
        self.make_request.assert_called_with("Datacenter.json")
        self.assertEqual('dal01', r)

    def test_w_param(self):
        self.make_request.return_value = '[123]'
        r = self.metadata.get('vlans', '1:2:3:4:5')
        self.make_request.assert_called_with("Vlans/1:2:3:4:5.json")
        self.assertEqual([123], r)

    def test_user_data(self):
        self.make_request.return_value = 'user_data'
        r = self.metadata.get('user_data')
        self.make_request.assert_called_with("UserMetadata.txt")
        self.assertEqual('user_data', r)

    def test_return_none(self):
        self.make_request.return_value = None
        r = self.metadata.get('datacenter')
        self.make_request.assert_called_with("Datacenter.json")
        self.assertEqual(None, r)

    def test_w_param_error(self):
        self.assertRaises(SoftLayer.SoftLayerError, self.metadata.get, 'vlans')

    def test_not_exists(self):
        self.assertRaises(
            SoftLayer.SoftLayerError, self.metadata.get, 'something')

    def test_networks_not_exist(self):
        self.make_request.return_value = '[]'
        r = self.metadata.public_network()
        self.assertEqual({'mac_addresses': []}, r)

    def test_networks(self):
        resp = '["list", "of", "stuff"]'
        resp_list = ['list', 'of', 'stuff']
        self.make_request.return_value = resp
        r = self.metadata.public_network()
        self.assertEqual({
            'vlan_ids': resp_list,
            'router': resp_list,
            'vlans': resp_list,
            'mac_addresses': resp_list
        }, r)

        r = self.metadata.private_network()
        self.assertEqual({
            'vlan_ids': resp_list,
            'router': resp_list,
            'vlans': resp_list,
            'mac_addresses': resp_list
        }, r)


class MetadataTestsMakeRequest(unittest.TestCase):

    def setUp(self):
        self.metadata = SoftLayer.MetadataManager()
        self.url = '/'.join([
            SoftLayer.consts.API_PRIVATE_ENDPOINT_REST.rstrip('/'),
            'SoftLayer_Resource_Metadata',
            'something.json'])

    @patch('SoftLayer.metadata.make_rest_api_call')
    def test_basic(self, make_api_call):
        r = self.metadata.make_request('something.json')
        make_api_call.assert_called_with(
            'GET', self.url,
            timeout=5,
            http_headers={'User-Agent': 'SoftLayer Python v2.2.0'})
        self.assertEqual(make_api_call(), r)

    @patch('SoftLayer.metadata.make_rest_api_call')
    def test_raise_error(self, make_api_call):
        make_api_call.side_effect = SoftLayer.SoftLayerAPIError(
            'faultCode', 'faultString')
        self.assertRaises(
            SoftLayer.SoftLayerAPIError,
            self.metadata.make_request, 'something.json')

    @patch('SoftLayer.metadata.make_rest_api_call')
    def test_raise_404_error(self, make_api_call):
        make_api_call.side_effect = SoftLayer.SoftLayerAPIError(
            404, 'faultString')
        r = self.metadata.make_request('something.json')
        self.assertEqual(r, None)
