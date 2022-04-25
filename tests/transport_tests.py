"""
    SoftLayer.tests.transport_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import io
import json
from unittest import mock as mock
import warnings

import pytest
import requests

import SoftLayer
from SoftLayer import consts
from SoftLayer import testing
from SoftLayer import transports


class TestFixtureTransport(testing.TestCase):

    def set_up(self):
        self.transport = transports.FixtureTransport()

    def test_basic(self):
        req = transports.Request()
        req.service = 'SoftLayer_Account'
        req.method = 'getObject'
        resp = self.transport(req)
        self.assertEqual(resp['accountId'], 1234)

    def test_no_module(self):
        req = transports.Request()
        req.service = 'Doesnt_Exist'
        req.method = 'getObject'
        self.assertRaises(NotImplementedError, self.transport, req)

    def test_no_method(self):
        req = transports.Request()
        req.service = 'SoftLayer_Account'
        req.method = 'getObjectzzzz'
        self.assertRaises(NotImplementedError, self.transport, req)


class TestTimingTransport(testing.TestCase):

    def set_up(self):
        fixture_transport = transports.FixtureTransport()
        self.transport = transports.TimingTransport(fixture_transport)

    def test_call(self):
        req = transports.Request()
        req.service = 'SoftLayer_Account'
        req.method = 'getObject'
        resp = self.transport(req)
        self.assertEqual(resp['accountId'], 1234)

    def test_get_last_calls(self):
        req = transports.Request()
        req.service = 'SoftLayer_Account'
        req.method = 'getObject'
        resp = self.transport(req)
        self.assertEqual(resp['accountId'], 1234)
        calls = self.transport.get_last_calls()
        self.assertEqual(calls[0][0].service, 'SoftLayer_Account')

    def test_print_reproduceable(self):
        req = transports.Request()
        req.service = 'SoftLayer_Account'
        req.method = 'getObject'
        output_text = self.transport.print_reproduceable(req)
        self.assertEqual('SoftLayer_Account', output_text)


class TestDebugTransport(testing.TestCase):

    def set_up(self):
        fixture_transport = transports.FixtureTransport()
        self.transport = transports.DebugTransport(fixture_transport)
        req = transports.Request()
        req.service = 'SoftLayer_Account'
        req.method = 'getObject'
        self.req = req

    def test_call(self):

        resp = self.transport(self.req)
        self.assertEqual(resp['accountId'], 1234)

    def test_get_last_calls(self):

        resp = self.transport(self.req)
        self.assertEqual(resp['accountId'], 1234)
        calls = self.transport.get_last_calls()
        self.assertEqual(calls[0].service, 'SoftLayer_Account')

    def test_print_reproduceable(self):
        req = transports.Request()
        req.service = 'SoftLayer_Account'
        req.method = 'getObject'
        output_text = self.transport.print_reproduceable(self.req)
        self.assertEqual('SoftLayer_Account', output_text)

    def test_print_reproduceable_post(self):
        req = transports.Request()
        req.url = "https://test.com"
        req.payload = "testing"
        req.transport_headers = {"test-headers": 'aaaa'}
        req.args = 'createObject'

        rest_transport = transports.RestTransport()
        transport = transports.DebugTransport(rest_transport)

        output_text = transport.print_reproduceable(req)

        self.assertIn("https://test.com", output_text)
        self.assertIn("-X POST", output_text)

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_error(self, request):
        # Test JSON Error
        e = requests.HTTPError('error')
        e.response = mock.MagicMock()
        e.response.status_code = 404
        e.response.text = '''{
            "error": "description",
            "code": "Error Code"
        }'''
        request().raise_for_status.side_effect = e

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        rest_transport = transports.RestTransport()
        transport = transports.DebugTransport(rest_transport)
        self.assertRaises(SoftLayer.SoftLayerAPIError, transport, req)
        calls = transport.get_last_calls()
        self.assertEqual(404, calls[0].exception.faultCode)
