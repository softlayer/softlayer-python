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


class TestXmlRpcAPICall(testing.TestCase):

    def set_up(self):
        self.transport = SoapTransport(endpoint_url='https://api.softlayer.com/soap/v3.1/')
        self.response = get_soap_response()
        self.user = os.getenv('SL_USER')
        self.password = os.environ.get('SL_APIKEY')

    def test_call(self):
        request = Request()
        request.service = 'SoftLayer_Account'
        request.method = 'getObject'
        request.transport_user = self.user
        request.transport_password = self.password
        data = self.transport(request)
        pp(data)
        self.assertEqual(data.get('id'), 307608)

