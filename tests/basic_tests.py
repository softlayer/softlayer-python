import SoftLayer.API
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import os


def get_creds():
    return {
        'username': os.environ['SL_USERNAME'],
        'api_key': os.environ['SL_API_KEY']
    }


class UnauthedUser(unittest.TestCase):
    def test_failed_auth(self):
        client = SoftLayer.API.Client('SoftLayer_User_Customer',
            None,
            'doesnotexist',
            'issurelywrong',
            timeout=20)
        self.assertRaises(SoftLayer.API.SoftLayerError, client.getPortalLoginToken)


class AuthedUser(unittest.TestCase):
    def test_result_types(self):
        creds = get_creds()
        client = SoftLayer.API.Client('SoftLayer_User_Security_Question',
            None,
            creds['username'],
            creds['api_key'],
            timeout=20)
        result = client.getAllObjects()
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIsInstance(result[0]['viewable'], int)
        self.assertIsInstance(result[0]['question'], str)
        self.assertIsInstance(result[0]['id'], int)
        self.assertIsInstance(result[0]['displayOrder'], int)
