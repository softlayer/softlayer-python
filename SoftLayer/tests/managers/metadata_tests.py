"""
    SoftLayer.tests.managers.metadata_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

import SoftLayer
from SoftLayer import consts
from SoftLayer import testing


class MetadataTests(testing.TestCase):

    def set_up(self):
        self.metadata = SoftLayer.MetadataManager()

    @mock.patch('SoftLayer.transports.make_rest_api_call')
    def test_get(self, make_request):
        make_request.return_value = 'dal01'
        resp = self.metadata.get('datacenter')

        self.assertEqual('dal01', resp)

        (request, ), kwargs = make_request.call_args

        self.assertEqual(request.endpoint, self.metadata.url)
        self.assertEqual(request.service, 'SoftLayer_Resource_Metadata')
        self.assertEqual(request.method, 'Datacenter')
        self.assertEqual(request.transport_headers,
                         {'User-Agent': consts.USER_AGENT})
        self.assertEqual(request.timeout, self.metadata.timeout)
        self.assertEqual(request.identifier, None)
        self.assertEqual(kwargs['extension'], 'json')

    @mock.patch('SoftLayer.transports.make_rest_api_call')
    def test_no_param(self, make_request):
        make_request.return_value = 'dal01'

        resp = self.metadata.get('datacenter')

        self.assertEqual('dal01', resp)
        (request, ), kwargs = make_request.call_args
        self.assertEqual(request.method, 'Datacenter')
        self.assertEqual(request.identifier, None)

    @mock.patch('SoftLayer.transports.make_rest_api_call')
    def test_w_param(self, make_request):
        make_request.return_value = [123]
        resp = self.metadata.get('vlans', '1:2:3:4:5')

        self.assertEqual([123], resp)
        (request, ), kwargs = make_request.call_args
        self.assertEqual(request.method, 'Vlans')
        self.assertEqual(request.identifier, '1:2:3:4:5')

    @mock.patch('SoftLayer.transports.make_rest_api_call')
    def test_user_data(self, make_request):
        make_request.return_value = 'user_data'
        resp = self.metadata.get('user_data')

        self.assertEqual('user_data', resp)
        (request, ), kwargs = make_request.call_args
        self.assertEqual(request.method, 'UserMetadata')
        self.assertEqual(request.identifier, None)
        self.assertEqual(kwargs['extension'], 'txt')

    @mock.patch('SoftLayer.transports.make_rest_api_call')
    def test_return_none(self, make_request):
        make_request.return_value = None
        resp = self.metadata.get('datacenter')

        self.assertEqual(None, resp)

    @mock.patch('SoftLayer.transports.make_rest_api_call')
    def test_404(self, make_request):
        make_request.side_effect = SoftLayer.SoftLayerAPIError(404,
                                                               'Not Found')
        resp = self.metadata.get('user_data')

        self.assertEqual(None, resp)

    @mock.patch('SoftLayer.transports.make_rest_api_call')
    def test_error(self, make_request):
        exception = SoftLayer.SoftLayerAPIError(500, 'Error')
        make_request.side_effect = exception

        self.assertRaises(SoftLayer.SoftLayerAPIError,
                          self.metadata.get, 'user_data')

    @mock.patch('SoftLayer.transports.make_rest_api_call')
    def test_w_param_error(self, make_request):
        self.assertRaises(SoftLayer.SoftLayerError, self.metadata.get, 'vlans')

    @mock.patch('SoftLayer.transports.make_rest_api_call')
    def test_not_exists(self, make_request):
        self.assertRaises(SoftLayer.SoftLayerError,
                          self.metadata.get,
                          'something')

    @mock.patch('SoftLayer.transports.make_rest_api_call')
    def test_networks_not_exist(self, make_request):
        make_request.return_value = []
        r = self.metadata.public_network()
        self.assertEqual({'mac_addresses': []}, r)

    @mock.patch('SoftLayer.transports.make_rest_api_call')
    def test_networks(self, make_request):
        resp = ['list', 'of', 'stuff']
        make_request.return_value = resp
        r = self.metadata.public_network()
        self.assertEqual({
            'vlan_ids': resp,
            'router': resp,
            'vlans': resp,
            'mac_addresses': resp
        }, r)

        r = self.metadata.private_network()
        self.assertEqual({
            'vlan_ids': resp,
            'router': resp,
            'vlans': resp,
            'mac_addresses': resp
        }, r)
