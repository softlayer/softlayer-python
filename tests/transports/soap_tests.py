"""
    SoftLayer.tests.transports.xmlrc
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import io
import json
from unittest import mock as mock
import os
import warnings

import pytest
import requests

import SoftLayer
from SoftLayer import consts
from SoftLayer import testing
from SoftLayer.transports.soap import SoapTransport
from SoftLayer.transports import Request


from pprint import pprint as pp


def get_soap_response():
    response = requests.Response()
    list_body = b'''<?xml version="1.0" encoding="utf-8"?>
<params>
<param>
<value>
<array>
<data/>
</array>
</value>
</param>
</params>'''
    response.raw = io.BytesIO(list_body)
    response.headers['SoftLayer-Total-Items'] = 10
    response.status_code = 200
    return response


class TestSoapAPICall(testing.TestCase):

    def set_up(self):
        self.transport = SoapTransport(endpoint_url='https://api.softlayer.com/soap/v3.1/')
        self.response = get_soap_response()
        self.user = os.getenv('SL_USER')
        self.password = os.environ.get('SL_APIKEY')
        request = Request()
        request.service = 'SoftLayer_Account'
        request.method = 'getObject'
        request.transport_user = self.user
        request.transport_password = self.password
        self.request = request

    def test_call(self):

        data = self.transport(self.request)
        pp(data)
        self.assertEqual(data.get('id'), 307608)
        self.assertEqual(data.get('companyName'), "SoftLayer Internal - Development Community")

    # def test_debug_call(self):

    #     self.request.mask = "mask[id,accountName,companyName]"
    #     data = self.transport(self.request)

    #     self.assertEqual(data.get('id'), 307608)
    #     debug_data = self.transport.print_reproduceable(self.request)
    #     print(debug_data['envelope'])
    #     self.assertEqual(":sdfsdf", debug_data)

    def test_objectMask(self):
        self.request.mask = "mask[id,companyName]"
        data = self.transport(self.request)
        pp(data)
        self.assertEqual(data.get('companyName'), "SoftLayer Internal - Development Community")
        self.assertIsNone(data.get('address1'))
        self.assertEqual(data.get('id'), 307608)

    def test_objectFilter(self):
        self.request.service = "SoftLayer_Product_Package"
        self.request.method = "getAllObjects"
        self.request.mask = "mask[id,description,keyName,type[id,keyName],name]"
        self.request.filter = {'type': {'keyName': {'operation': 'BARE_METAL_CPU'}}}
        self.request.limit = 5
        self.request.offset = 0
        data = self.transport(self.request)
        # pp(data)
        # print("^^^ DATA **** ")
        for package in data:

            self.assertEqual(package.get('type').get('keyName'), "BARE_METAL_CPU")

    def test_virtualGuest(self):
        accountRequest = Request()
        accountRequest.service = "SoftLayer_Account"
        accountRequest.method = "getVirtualGuests"
        accountRequest.limit = 5
        accountRequest.offset = 0
        accountRequest.mask = "mask[id,hostname,domain]"
        accountRequest.transport_user = self.user
        accountRequest.transport_password = self.password

        vsis = self.transport(accountRequest)
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

    # TODO MORE COMPLEX OBJECT FILTERS!
