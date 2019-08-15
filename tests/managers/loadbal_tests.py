"""
    SoftLayer.tests.managers.loadbal_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import testing


class LoadBalancerTests(testing.TestCase):

    def set_up(self):
        self.lb_mgr = SoftLayer.LoadBalancerManager(self.client)

    def test_get_adcs(self):
        self.lb_mgr.get_adcs()
        self.assert_called_with('SoftLayer_Account', 'getApplicationDeliveryControllers')

    def test_get_adc_masks(self):
        self.lb_mgr.get_adcs(mask="mask[id]")
        self.assert_called_with('SoftLayer_Account', 'getApplicationDeliveryControllers', mask="mask[id]")

    def test_get_adc(self):
        self.lb_mgr.get_adc(1234)
        self.assert_called_with('SoftLayer_Network_Application_Delivery_Controller', 'getObject', identifier=1234)

    def test_get_adc_mask(self):
        self.lb_mgr.get_adc(1234, mask="mask[id]")
        self.assert_called_with('SoftLayer_Network_Application_Delivery_Controller', 'getObject', identifier=1234,
                                mask="mask[id]")

    def test_get_lbaas(self):
        self.lb_mgr.get_lbaas()
        self.assert_called_with('SoftLayer_Network_LBaaS_LoadBalancer', 'getAllObjects')

    def test_get_lbaas_mask(self):
        self.lb_mgr.get_lbaas(mask="mask[id]")
        self.assert_called_with('SoftLayer_Network_LBaaS_LoadBalancer', 'getAllObjects', mask="mask[id]")

    def test_get_lb(self):
        lb = self.lb_mgr.get_lb(1234)
        self.assert_called_with('SoftLayer_Network_LBaaS_LoadBalancer', 'getObject', identifier=1234)
        self.assert_called_with('SoftLayer_Network_LBaaS_LoadBalancer', 'getLoadBalancerMemberHealth',
                                args=(lb.get('uuid'),))
        self.assertIsNotNone(lb['health'])

    def test_get_lb_mask(self):
        lb = self.lb_mgr.get_lb(1234, mask="mask[id]")
        self.assert_called_with('SoftLayer_Network_LBaaS_LoadBalancer', 'getObject', identifier=1234, mask="mask[id]")
        self.assert_called_with('SoftLayer_Network_LBaaS_LoadBalancer', 'getLoadBalancerMemberHealth',
                                args=(lb.get('uuid'),))
        self.assertIsNotNone(lb['health'])

