"""
    SoftLayer.tests.transports.soap
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import io
import os
import requests
from unittest import mock as mock

from SoftLayer import testing
from SoftLayer.transports import Request
from SoftLayer.transports.soap import SoapTransport


def setup_response(filename, status_code=200, total_items=1):
    basepath = os.path.dirname(__file__)
    body = b''
    print(f"Base Path: {basepath}")
    with open(f"{basepath}/../../SoftLayer/fixtures/soap/{filename}.soap", 'rb') as fixture:
        body = fixture.read()
    response = requests.Response()
    list_body = body
    response.raw = io.BytesIO(list_body)
    response.headers['SoftLayer-Total-Items'] = total_items
    response.status_code = status_code
    return response


class TestSoapAPICall(testing.TestCase):

    def set_up(self):
        self.transport = SoapTransport(endpoint_url='https://api.softlayer.com/soap/v3.1/')

        self.user = "testUser"
        self.password = "testPassword"
        # self.user = os.getenv('SL_USER')
        # self.password = os.environ.get('SL_APIKEY')
        request = Request()
        request.service = 'SoftLayer_Account'
        request.method = 'getObject'
        request.transport_user = self.user
        request.transport_password = self.password
        self.request = request

    @mock.patch('requests.Session.post')
    def test_call(self, zeep_post):
        zeep_post.return_value = setup_response('SoftLayer_Account_getObject')
        self.request.mask = "mask[id,companyName]"
        data = self.transport(self.request)
        self.assertEqual(data.get('id'), 307608)
        self.assertEqual(data.get('companyName'), "SoftLayer Internal - Development Community")

    # def test_debug_call(self):

    #     self.request.mask = "mask[id,accountName,companyName]"
    #     data = self.transport(self.request)

    #     self.assertEqual(data.get('id'), 307608)
    #     debug_data = self.transport.print_reproduceable(self.request)
    #     print(debug_data['envelope'])
    #     self.assertEqual(":sdfsdf", debug_data)

    @mock.patch('requests.Session.post')
    def test_objectMask(self, zeep_post):
        zeep_post.return_value = setup_response('test_objectMask')
        self.request.mask = "mask[id,companyName]"
        data = self.transport(self.request)
        self.assertEqual(data.get('companyName'), "SoftLayer Internal - Development Community")
        self.assertIsNone(data.get('address1'))
        self.assertEqual(data.get('id'), 307608)

    @mock.patch('requests.Session.post')
    def test_objectFilter(self, zeep_post):
        zeep_post.return_value = setup_response('test_objectFilter')
        self.request.service = "SoftLayer_Product_Package"
        self.request.method = "getAllObjects"
        self.request.mask = "mask[id,description,keyName,type[id,keyName],name]"
        self.request.filter = {'type': {'keyName': {'operation': 'BARE_METAL_CPU'}}}
        self.request.limit = 5
        self.request.offset = 0
        data = self.transport(self.request)
        for package in data:
            self.assertEqual(package.get('type').get('keyName'), "BARE_METAL_CPU")

    @mock.patch('requests.Session.post')
    def test_virtualGuest(self, zeep_post):
        zeep_post.side_effect = [
            setup_response('SoftLayer_Account_getVirtualGuests'),
            setup_response('SoftLayer_Virtual_Guest_getObject')
        ]
        accountRequest = Request()
        accountRequest.service = "SoftLayer_Account"
        accountRequest.method = "getVirtualGuests"
        accountRequest.limit = 5
        accountRequest.offset = 0
        accountRequest.mask = "mask[id,hostname,domain]"
        accountRequest.transport_user = self.user
        accountRequest.transport_password = self.password

        vsis = self.transport(accountRequest)
        self.assertEqual(1, len(vsis))
        for vsi in vsis:
            self.assertGreater(vsi.get('id'), 1)
            vsiRequest = Request()
            vsiRequest.service = "SoftLayer_Virtual_Guest"
            vsiRequest.method = "getObject"
            vsiRequest.identifier = vsi.get('id')
            vsiRequest.mask = "mask[id,hostname,domain]"
            vsiRequest.transport_user = self.user
            vsiRequest.transport_password = self.password
            thisVsi = self.transport(vsiRequest)
            self.assertEqual(thisVsi.get('id'), vsi.get('id'))

    # NEXT MORE COMPLEX OBJECT FILTERS!
