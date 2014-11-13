"""
    softlayer.tests.auth_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from softlayer import auth
from softlayer import testing
from softlayer import transports


class TestAuthenticationBase(testing.TestCase):
    def test_get_request(self):
        auth_base = auth.AuthenticationBase()
        self.assertEqual(auth_base.get_request({}), {})
        self.assertEqual(auth_base.get_headers(), {})


class TestBasicAuthentication(testing.TestCase):
    def set_up(self):
        self.auth = auth.BasicAuthentication('USERNAME', 'APIKEY')

    def test_attribs(self):
        self.assertEqual(self.auth.username, 'USERNAME')
        self.assertEqual(self.auth.api_key, 'APIKEY')

    def test_get_request(self):
        req = transports.Request()
        authed_req = self.auth.get_request(req)
        self.assertEqual(authed_req.headers, {
            'authenticate': {
                'username': 'USERNAME',
                'apiKey': 'APIKEY',
            }
        })

    def test_repr(self):
        s = repr(self.auth)
        self.assertIn('BasicAuthentication', s)
        self.assertIn('USERNAME', s)


class TestTokenAuthentication(testing.TestCase):
    def set_up(self):
        self.auth = auth.TokenAuthentication(12345, 'TOKEN')

    def test_attribs(self):
        self.assertEqual(self.auth.user_id, 12345)
        self.assertEqual(self.auth.auth_token, 'TOKEN')

    def test_get_request(self):
        req = transports.Request()
        authed_req = self.auth.get_request(req)
        self.assertEqual(authed_req.headers, {
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
