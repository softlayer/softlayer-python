"""
    SoftLayer.tests.managers.metadata_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import SoftLayer
from SoftLayer import testing


class MetadataTests(testing.TestCase):

    def set_up(self):
        self.metadata = SoftLayer.MetadataManager(client=self.client)

    def test_get(self):
        mock = self.set_mock('SoftLayer_Resource_Metadata', 'Datacenter')
        mock.return_value = 'dal01'
        resp = self.metadata.get('datacenter')

        self.assertEqual('dal01', resp)
        self.assert_called_with('SoftLayer_Resource_Metadata', 'Datacenter',
                                identifier=None)

    def test_no_param(self):
        resp = self.metadata.get('datacenter')

        self.assertEqual('dal01', resp)
        self.assert_called_with('SoftLayer_Resource_Metadata', 'Datacenter',
                                identifier=None,
                                args=tuple())

    def test_w_param(self):
        resp = self.metadata.get('vlans', '1:2:3:4:5')

        self.assertEqual([10, 124], resp)
        self.assert_called_with('SoftLayer_Resource_Metadata', 'Vlans',
                                args=('1:2:3:4:5',))

    def test_user_data(self):
        resp = self.metadata.get('user_data')

        self.assertEqual(resp, 'User-supplied data')
        self.assert_called_with('SoftLayer_Resource_Metadata', 'UserMetadata',
                                identifier=None)

    def test_return_none(self):
        mock = self.set_mock('SoftLayer_Resource_Metadata', 'Datacenter')
        mock.return_value = None

        resp = self.metadata.get('datacenter')

        self.assertEqual(None, resp)

    def test_404(self):
        mock = self.set_mock('SoftLayer_Resource_Metadata', 'UserMetadata')
        mock.side_effect = SoftLayer.SoftLayerAPIError(404, 'Not Found')
        resp = self.metadata.get('user_data')

        self.assertEqual(None, resp)

    def test_error(self):
        exception = SoftLayer.SoftLayerAPIError(500, 'Error')
        mock = self.set_mock('SoftLayer_Resource_Metadata', 'UserMetadata')
        mock.side_effect = exception

        self.assertRaises(SoftLayer.SoftLayerAPIError,
                          self.metadata.get, 'user_data')

    def test_w_param_error(self):
        self.assertRaises(SoftLayer.SoftLayerError, self.metadata.get, 'vlans')

    def test_not_exists(self):
        self.assertRaises(SoftLayer.SoftLayerError,
                          self.metadata.get,
                          'something')

    def test_networks(self):
        r = self.metadata.public_network()
        self.assertEqual({
            'vlan_ids': [8384, 12446],
            'router': 'brc01',
            'vlans': [10, 124],
            'mac_addresses': ['06-00-00-00-00-00'],
        }, r)

        r = self.metadata.private_network()
        self.assertEqual({
            'vlan_ids': [8384, 12446],
            'router': 'brc01',
            'vlans': [10, 124],
            'mac_addresses': ['07-00-00-00-00-00'],
        }, r)
