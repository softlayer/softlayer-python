"""
    SoftLayer.tests.API.functional_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import SoftLayer
import os

try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA
from mock import patch
from SoftLayer.transport import xmlrpclib_transport


def get_creds():
    for key in 'SL_USERNAME SL_API_KEY'.split():
        if key not in os.environ:
            raise unittest.SkipTest(
                'SL_USERNAME and SL_API_KEY environmental variables not set')

    return {
        'endpoint': (os.environ.get('SL_API_ENDPOINT') or
                     SoftLayer.API_PUBLIC_ENDPOINT),
        'username': os.environ['SL_USERNAME'],
        'api_key': os.environ['SL_API_KEY']
    }


class UnauthedUser(unittest.TestCase):
    def test_failed_auth(self):
        client = SoftLayer.Client(
            'SoftLayer_User_Customer', None, 'doesnotexist', 'issurelywrong',
            timeout=20)
        self.assertRaises(SoftLayer.SoftLayerAPIError,
                          client.getPortalLoginToken)

    @patch('SoftLayer.API.make_api_call', xmlrpclib_transport.make_api_call)
    def test_with_xmlrpc_transport(self):
        client = SoftLayer.Client(
            'SoftLayer_User_Customer', None, 'doesnotexist', 'issurelywrong',
            timeout=20)
        self.assertRaises(SoftLayer.SoftLayerAPIError,
                          client.getPortalLoginToken)

    def test_404(self):
        client = SoftLayer.Client(
            'SoftLayer_User_Customer', None, 'doesnotexist', 'issurelywrong',
            timeout=20, endpoint_url='http://httpbin.org/status/404')

        try:
            client.doSomething()
        except SoftLayer.SoftLayerAPIError, e:
            self.assertEqual(e.faultCode, 404)
            self.assertIn('NOT FOUND', e.faultString)
            self.assertIn('NOT FOUND', e.reason)
        except:
            self.fail('No Exception Raised')

    @patch('SoftLayer.API.make_api_call', xmlrpclib_transport.make_api_call)
    def test_404_with_xmlrpc_transport(self):
        client = SoftLayer.Client(
            'SoftLayer_User_Customer', None, 'doesnotexist', 'issurelywrong',
            timeout=20, endpoint_url='http://httpbin.org/status/404')

        try:
            client.doSomething()
        except SoftLayer.SoftLayerAPIError, e:
            self.assertEqual(e.faultCode, 404)
            self.assertIn('NOT FOUND', e.faultString)
            self.assertIn('NOT FOUND', e.reason)

    def test_no_hostname(self):
        try:
            # This test will fail if 'notvalidsoftlayer.com' becomes a thing
            SoftLayer.API.make_api_call(
                'http://notvalidsoftlayer.com', 'getObject')
        except SoftLayer.SoftLayerAPIError, e:
            self.assertEqual(e.faultCode, 0)
            self.assertIn('not known', e.faultString)
            self.assertIn('not known', e.reason)
        except:
            self.fail('No Exception Raised')

    def test_no_hostname_with_xmlrpc_transport(self):
        try:
            # This test will fail if 'notvalidsoftlayer.com' becomes a thing
            xmlrpclib_transport.make_api_call(
                'http://notvalidsoftlayer.com', 'getObject')
        except SoftLayer.SoftLayerAPIError, e:
            self.assertEqual(e.faultCode, 0)
            self.assertIn('not known', e.faultString)
            self.assertIn('not known', e.reason)
        except:
            self.fail('No Exception Raised')


class AuthedUser(unittest.TestCase):
    def test_service_does_not_exist(self):
        creds = get_creds()
        client = SoftLayer.Client(
            username=creds['username'],
            api_key=creds['api_key'],
            endpoint_url=creds['endpoint'],
            timeout=20)

        try:
            client["SoftLayer_DOESNOTEXIST"].getObject()
        except SoftLayer.SoftLayerAPIError, e:
            self.assertEqual(e.faultCode, '-32601')
            self.assertEqual(e.faultString, 'Service does not exist')
            self.assertEqual(e.reason, 'Service does not exist')
        except:
            self.fail('No Exception Raised')

    def test_dns(self):
        creds = get_creds()
        client = SoftLayer.Client(
            username=creds['username'],
            api_key=creds['api_key'],
            endpoint_url=creds['endpoint'],
            timeout=20)
        client["SoftLayer_Dns_Domain"].getByDomainName('p.sftlyr.ws')

    def test_result_types(self):
        creds = get_creds()
        client = SoftLayer.Client(
            'SoftLayer_User_Security_Question',
            username=creds['username'],
            api_key=creds['api_key'],
            endpoint_url=creds['endpoint'],
            timeout=20)
        result = client.getAllObjects()
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIsInstance(result[0]['viewable'], int)
        self.assertIsInstance(result[0]['question'], str)
        self.assertIsInstance(result[0]['id'], int)
        self.assertIsInstance(result[0]['displayOrder'], int)
