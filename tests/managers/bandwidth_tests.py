"""
    SoftLayer.tests.managers.bandwidth_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from SoftLayer.managers.bandwidth import BandwidthManager as BandwidthManager
from SoftLayer import testing


class BandwidthManagerTests(testing.TestCase):

    def set_up(self):
        self.manager = BandwidthManager(self.client)

    def test_get_location_group(self):
        self.manager.get_location_group()
        _filter = {
            "locationGroupTypeId": {
                "operation": 1
            }
        }
        self.assert_called_with('SoftLayer_Location_Group', 'getAllObjects', filter=_filter)

    def test_create_pool(self):
        self.manager.create_pool(name_pool='New region', id_location_group=2)
        self.assert_called_with('SoftLayer_Network_Bandwidth_Version1_Allotment', 'createObject')
