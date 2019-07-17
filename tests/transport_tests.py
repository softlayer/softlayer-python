"""
    SoftLayer.tests.transport_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import io
import warnings

import mock
import pytest
import requests
import six

import SoftLayer
from SoftLayer import consts
from SoftLayer import testing
from SoftLayer import transports


def get_xmlrpc_response():
    response = requests.Response()
    list_body = six.b('''<?xml version="1.0" encoding="utf-8"?>
<params>
<param>
<value>
<array>
<data/>
</array>
</value>
</param>
</params>''')
    response.raw = io.BytesIO(list_body)
    response.headers['SoftLayer-Total-Items'] = 10
    response.status_code = 200
    return response


class TestXmlRpcAPICall(testing.TestCase):

    def set_up(self):
        self.transport = transports.XmlRpcTransport(
            endpoint_url='http://something.com',
        )
        self.response = get_xmlrpc_response()

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_call(self, request):
        request.return_value = self.response

        data = '''<?xml version='1.0'?>
<methodCall>
<methodName>getObject</methodName>
<params>
<param>
<value><struct>
<member>
<name>headers</name>
<value><struct>
</struct></value>
</member>
</struct></value>
</param>
</params>
</methodCall>
'''

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        resp = self.transport(req)

        request.assert_called_with('POST',
                                   'http://something.com/SoftLayer_Service',
                                   headers={'Content-Type': 'application/xml',
                                            'User-Agent': consts.USER_AGENT},
                                   proxies=None,
                                   data=data,
                                   timeout=None,
                                   cert=None,
                                   verify=True,
                                   auth=None)
        self.assertEqual(resp, [])
        self.assertIsInstance(resp, transports.SoftLayerListResult)
        self.assertEqual(resp.total_count, 10)

    def test_proxy_without_protocol(self):
        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        req.proxy = 'localhost:3128'

        try:
            self.assertRaises(SoftLayer.TransportError, self.transport, req)
        except AssertionError:
            warnings.warn("Incorrect Exception raised. Expected a "
                          "SoftLayer.TransportError error")

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_valid_proxy(self, request):
        request.return_value = self.response
        self.transport.proxy = 'http://localhost:3128'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        self.transport(req)

        request.assert_called_with(
            'POST',
            mock.ANY,
            proxies={'https': 'http://localhost:3128',
                     'http': 'http://localhost:3128'},
            data=mock.ANY,
            headers=mock.ANY,
            timeout=None,
            cert=None,
            verify=True,
            auth=None)

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_identifier(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.identifier = 1234
        self.transport(req)

        _, kwargs = request.call_args
        self.assertIn(
            """<member>
<name>id</name>
<value><int>1234</int></value>
</member>""", kwargs['data'])

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_filter(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.filter = {'TYPE': {'attribute': {'operation': '^= prefix'}}}
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn(
            """<member>
<name>operation</name>
<value><string>^= prefix</string></value>
</member>""", kwargs['data'])

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_limit_offset(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.limit = 10
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn("""<member>
<name>resultLimit</name>
<value><struct>
<member>""", kwargs['data'])
        self.assertIn("""<name>limit</name>
<value><int>10</int></value>
</member>""", kwargs['data'])

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_old_mask(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.mask = {"something": "nested"}
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn("""<member>
<name>mask</name>
<value><struct>
<member>
<name>something</name>
<value><string>nested</string></value>
</member>
</struct></value>
</member>""", kwargs['data'])

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_mask_call_no_mask_prefix(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.mask = "something.nested"
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn(
            "<value><string>mask[something.nested]</string></value>",
            kwargs['data'])

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_mask_call_v2(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.mask = "mask[something[nested]]"
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn(
            "<value><string>mask[something[nested]]</string></value>",
            kwargs['data'])

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_mask_call_v2_dot(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.mask = "mask.something.nested"
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn("<value><string>mask.something.nested</string></value>",
                      kwargs['data'])

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_request_exception(self, request):
        # Test Text Error
        e = requests.HTTPError('error')
        e.response = mock.MagicMock()
        e.response.status_code = 404
        e.response.content = 'Error Code'
        request().raise_for_status.side_effect = e

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'

        self.assertRaises(SoftLayer.TransportError, self.transport, req)

    def test_print_reproduceable(self):
        req = transports.Request()
        req.url = "https://test.com"
        req.payload = "testing"
        req.transport_headers = {"test-headers": 'aaaa'}
        output_text = self.transport.print_reproduceable(req)
        self.assertIn("https://test.com", output_text)

    @mock.patch('SoftLayer.transports.requests.Session.request')
    @mock.patch('requests.auth.HTTPBasicAuth')
    def test_ibm_id_call(self, auth, request):
        request.return_value = self.response

        data = '''<?xml version='1.0'?>
<methodCall>
<methodName>getObject</methodName>
<params>
<param>
<value><struct>
<member>
<name>headers</name>
<value><struct>
</struct></value>
</member>
</struct></value>
</param>
</params>
</methodCall>
'''

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.transport_user = 'apikey'
        req.transport_password = '1234567890qweasdzxc'
        resp = self.transport(req)

        auth.assert_called_with('apikey', '1234567890qweasdzxc')
        request.assert_called_with('POST',
                                   'http://something.com/SoftLayer_Service',
                                   headers={'Content-Type': 'application/xml',
                                            'User-Agent': consts.USER_AGENT},
                                   proxies=None,
                                   data=data,
                                   timeout=None,
                                   cert=None,
                                   verify=True,
                                   auth=mock.ANY)
        self.assertEqual(resp, [])
        self.assertIsInstance(resp, transports.SoftLayerListResult)
        self.assertEqual(resp.total_count, 10)


@mock.patch('SoftLayer.transports.requests.Session.request')
@pytest.mark.parametrize(
    "transport_verify,request_verify,expected",
    [
        (True, True, True),
        (True, False, False),
        (True, None, True),

        (False, True, True),
        (False, False, False),
        (False, None, False),

        (None, True, True),
        (None, False, False),
        (None, None, True),
    ]
)
def test_verify(request,
                transport_verify,
                request_verify,
                expected):
    request.return_value = get_xmlrpc_response()

    transport = transports.XmlRpcTransport(
        endpoint_url='http://something.com',
    )

    req = transports.Request()
    req.service = 'SoftLayer_Service'
    req.method = 'getObject'

    if request_verify is not None:
        req.verify = request_verify

    if transport_verify is not None:
        transport.verify = transport_verify

    transport(req)

    request.assert_called_with('POST',
                               'http://something.com/SoftLayer_Service',
                               data=mock.ANY,
                               headers=mock.ANY,
                               cert=mock.ANY,
                               proxies=mock.ANY,
                               timeout=mock.ANY,
                               verify=expected,
                               auth=None)


class TestRestAPICall(testing.TestCase):

    def set_up(self):
        self.transport = transports.RestTransport(
            endpoint_url='http://something.com',
        )

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_basic(self, request):
        request().content = '[]'
        request().text = '[]'
        request().headers = requests.structures.CaseInsensitiveDict({
            'SoftLayer-Total-Items': '10',
        })

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        resp = self.transport(req)

        self.assertEqual(resp, [])
        self.assertIsInstance(resp, transports.SoftLayerListResult)
        self.assertEqual(resp.total_count, 10)
        request.assert_called_with(
            'GET', 'http://something.com/SoftLayer_Service/Resource.json',
            headers=mock.ANY,
            auth=None,
            data=None,
            params={},
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_http_and_json_error(self, request):
        # Test JSON Error
        e = requests.HTTPError('error')
        e.response = mock.MagicMock()
        e.response.status_code = 404
        e.response.text = '''
            "error": "description",
            "code": "Error Code"
        '''
        request().raise_for_status.side_effect = e

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        self.assertRaises(SoftLayer.SoftLayerAPIError, self.transport, req)

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_http_and_empty_error(self, request):
        # Test JSON Error
        e = requests.HTTPError('error')
        e.response = mock.MagicMock()
        e.response.status_code = 404
        e.response.text = ''
        request().raise_for_status.side_effect = e

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        self.assertRaises(SoftLayer.SoftLayerAPIError, self.transport, req)

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_empty_error(self, request):
        # Test empty response error.
        request().text = ''

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        self.assertRaises(SoftLayer.SoftLayerAPIError, self.transport, req)

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_json_error(self, request):
        # Test non-json response error.
        request().text = 'Not JSON'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        self.assertRaises(SoftLayer.SoftLayerAPIError, self.transport, req)

    def test_proxy_without_protocol(self):
        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        req.proxy = 'localhost:3128'

        try:
            self.assertRaises(SoftLayer.TransportError, self.transport, req)
        except AssertionError:
            warnings.warn("AssertionError raised instead of a SoftLayer.TransportError error")

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_valid_proxy(self, request):
        request().text = '{}'
        self.transport.proxy = 'http://localhost:3128'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'

        self.transport(req)

        request.assert_called_with(
            'GET', 'http://something.com/SoftLayer_Service/Resource.json',
            proxies={'https': 'http://localhost:3128',
                     'http': 'http://localhost:3128'},
            auth=None,
            data=None,
            params={},
            verify=True,
            cert=None,
            timeout=mock.ANY,
            headers=mock.ANY)

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_with_id(self, request):
        request().text = '{}'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.identifier = 2

        resp = self.transport(req)

        self.assertEqual(resp, {})
        request.assert_called_with(
            'GET',
            'http://something.com/SoftLayer_Service/2/getObject.json',
            headers=mock.ANY,
            auth=None,
            data=None,
            params={},
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_with_args(self, request):
        request().text = '{}'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.args = ('test', 1)

        resp = self.transport(req)

        self.assertEqual(resp, {})
        request.assert_called_with(
            'POST',
            'http://something.com/SoftLayer_Service/getObject.json',
            headers=mock.ANY,
            auth=None,
            data='{"parameters": ["test", 1]}',
            params={},
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_with_filter(self, request):
        request().text = '{}'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.filter = {'TYPE': {'attribute': {'operation': '^= prefix'}}}

        resp = self.transport(req)

        self.assertEqual(resp, {})
        request.assert_called_with(
            'GET',
            'http://something.com/SoftLayer_Service/getObject.json',
            params={'objectFilter':
                    '{"TYPE": {"attribute": {"operation": "^= prefix"}}}'},
            headers=mock.ANY,
            auth=None,
            data=None,
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_with_mask(self, request):
        request().text = '{}'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.mask = 'id,property'

        resp = self.transport(req)

        self.assertEqual(resp, {})
        request.assert_called_with(
            'GET',
            'http://something.com/SoftLayer_Service/getObject.json',
            params={'objectMask': 'mask[id,property]'},
            headers=mock.ANY,
            auth=None,
            data=None,
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

        # Now test with mask[] prefix
        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.mask = 'mask[id,property]'

        resp = self.transport(req)

        self.assertEqual(resp, {})
        request.assert_called_with(
            'GET',
            'http://something.com/SoftLayer_Service/getObject.json',
            params={'objectMask': 'mask[id,property]'},
            headers=mock.ANY,
            auth=None,
            data=None,
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_with_limit_offset(self, request):
        request().text = '{}'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.identifier = 2
        req.limit = 10
        req.offset = 5

        resp = self.transport(req)

        self.assertEqual(resp, {})
        request.assert_called_with(
            'GET',
            'http://something.com/SoftLayer_Service/2/getObject.json',
            headers=mock.ANY,
            auth=None,
            data=None,
            params={'resultLimit': '5,10'},
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

    @mock.patch('SoftLayer.transports.requests.Session.request')
    def test_unknown_error(self, request):
        e = requests.RequestException('error')
        e.response = mock.MagicMock()
        e.response.status_code = 404
        e.response.content = 'Error Code'
        request().raise_for_status.side_effect = e

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'

        self.assertRaises(SoftLayer.TransportError, self.transport, req)

    @mock.patch('SoftLayer.transports.requests.Session.request')
    @mock.patch('requests.auth.HTTPBasicAuth')
    def test_with_special_auth(self, auth, request):
        request().text = '{}'

        user = 'asdf'
        password = 'zxcv'
        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.identifier = 2
        req.transport_user = user
        req.transport_password = password

        resp = self.transport(req)
        self.assertEqual(resp, {})
        auth.assert_called_with(user, password)
        request.assert_called_with(
            'GET',
            'http://something.com/SoftLayer_Service/2/getObject.json',
            headers=mock.ANY,
            auth=mock.ANY,
            data=None,
            params={},
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

    def test_print_reproduceable(self):
        req = transports.Request()
        req.url = "https://test.com"
        req.payload = "testing"
        req.transport_headers = {"test-headers": 'aaaa'}
        output_text = self.transport.print_reproduceable(req)
        self.assertIn("https://test.com", output_text)


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
