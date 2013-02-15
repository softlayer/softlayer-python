import SoftLayer

try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA
from mock import patch, MagicMock
import urllib2


class MetadataTests(unittest.TestCase):

    def setUp(self):
        self.metadata = SoftLayer.MetadataManager()
        self.make_request = MagicMock()
        self.metadata.make_request = self.make_request

    def test_no_param(self):
        self.make_request.return_value = '"dal01"'
        r = self.metadata.get('datacenter')
        self.make_request.assert_called_with("Datacenter.json")
        self.assertEqual('dal01', r)

    def test_w_param(self):
        self.make_request.return_value = '[123]'
        r = self.metadata.get('vlans', '1:2:3:4:5')
        self.make_request.assert_called_with("Vlans/1:2:3:4:5.json")
        self.assertEqual([123], r)

    def test_w_param_error(self):
        self.assertRaises(SoftLayer.SoftLayerError, self.metadata.get, 'vlans')

    def test_not_exists(self):
        self.assertRaises(
            SoftLayer.SoftLayerError, self.metadata.get, 'something')


class MetadataTestsMakeRequest(unittest.TestCase):

    def setUp(self):
        self.metadata = SoftLayer.MetadataManager()
        self.url = '/'.join([
            SoftLayer.consts.API_PRIVATE_ENDPOINT_REST.rstrip('/'),
            'SoftLayer_Resource_Metadata',
            'something.json'])

    @patch('urllib2.Request')
    @patch('urllib2.urlopen')
    def test_basic(self, urlopen, req):
        r = self.metadata.make_request('something.json')
        req.assert_called_with(self.url)
        self.assertEqual(r, urlopen().read())

    @patch('urllib2.Request')
    @patch('urllib2.urlopen')
    def test_raise_httperror(self, urlopen, req):
        e = urllib2.HTTPError(
            'http://somewhere.com', 404, 'Error', {}, None)
        e.reason = 'Not Found'
        urlopen.side_effect = e
        self.assertRaises(
            SoftLayer.SoftLayerAPIError,
            self.metadata.make_request, 'something.json')

    @patch('urllib2.Request')
    @patch('urllib2.urlopen')
    def test_raise_urlerror(self, urlopen, req):
        urlopen.side_effect = urllib2.URLError('Error')
        self.assertRaises(
            SoftLayer.SoftLayerAPIError,
            self.metadata.make_request, 'something.json')
