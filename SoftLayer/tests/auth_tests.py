"""
    SoftLayer.tests.auth_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.auth import (
    AuthenticationBase, BasicAuthentication, TokenAuthentication)
from SoftLayer.tests import TestCase


class TestAuthenticationBase(TestCase):
    def test_get_headers(self):
        auth = AuthenticationBase()
        self.assertRaises(NotImplementedError, auth.get_headers)


class TestBasicAuthentication(TestCase):
    def set_up(self):
        self.auth = BasicAuthentication('USERNAME', 'APIKEY')

    def test_attribs(self):
        self.assertEquals(self.auth.username, 'USERNAME')
        self.assertEquals(self.auth.api_key, 'APIKEY')

    def test_get_headers(self):
        self.assertEquals(self.auth.get_headers(), {
            'authenticate': {
                'username': 'USERNAME',
                'apiKey': 'APIKEY',
            }
        })

    def test_repr(self):
        s = repr(self.auth)
        self.assertIn('BasicAuthentication', s)
        self.assertIn('USERNAME', s)


class TestTokenAuthentication(TestCase):
    def set_up(self):
        self.auth = TokenAuthentication(12345, 'TOKEN')

    def test_attribs(self):
        self.assertEquals(self.auth.user_id, 12345)
        self.assertEquals(self.auth.auth_token, 'TOKEN')

    def test_get_headers(self):
        self.assertEquals(self.auth.get_headers(), {
            'authenticate': {
                'complexType': 'PortalLoginToken',
                'userId': 12345,
                'authToken': 'TOKEN',
            }
        })

    def test_repr(self):
        s = repr(self.auth)
        self.assertIn('TokenAuthentication', s)
        self.assertIn('12345', s)
        self.assertIn('TOKEN', s)
