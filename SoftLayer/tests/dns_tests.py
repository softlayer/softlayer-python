import SoftLayer
import os

try:
    import unittest2 as unittest
except ImportError:
    import unittest
from mock import MagicMock


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


class DNSTests_unittests(unittest.TestCase):

    def setUp(self):
        self.client = MagicMock()
        self.dns_client = SoftLayer.DNSManager(self.client)

    def test_init_exercise(self):
        self.assertTrue(hasattr(self.dns_client, 'domain'))
        self.assertTrue(hasattr(self.dns_client, 'record'))

    def test_list_zones(self):
        zone_list = ['test']
        self.client.__getitem__().getObject.return_value = {
                'domains': zone_list}
        zones = self.dns_client.list_zones()
        self.assertEqual(zones, zone_list)
