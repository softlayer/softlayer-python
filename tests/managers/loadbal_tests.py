"""
    SoftLayer.tests.managers.loadbal_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import testing

VIRT_IP_SERVICE = ('SoftLayer_Network_Application_Delivery_Controller_'
                   'LoadBalancer_VirtualIpAddress')


class LoadBalancerTests(testing.TestCase):

    def set_up(self):
        self.lb_mgr = SoftLayer.LoadBalancerManager(self.client)

    def test_get_lb_pkgs(self):
        result = self.lb_mgr.get_lb_pkgs()

        self.assertEqual(len(result), 13)
        _filter = {
            'items': {
                'description': {
                    'operation': '*= Load Balancer'
                }
            }
        }
        self.assert_called_with('SoftLayer_Product_Package', 'getItems',
                                identifier=0,
                                filter=_filter)

    def test_get_hc_types(self):
        result = self.lb_mgr.get_hc_types()

        self.assertEqual(len(result), 6)
        service = ('SoftLayer_Network_Application_Delivery_Controller_'
                   'LoadBalancer_Health_Check_Type')
        self.assert_called_with(service, 'getAllObjects')

    def test_get_routing_methods(self):
        result = self.lb_mgr.get_routing_methods()

        self.assertEqual(len(result), 12)
        service = ('SoftLayer_Network_Application_Delivery_Controller_'
                   'LoadBalancer_Routing_Method')
        self.assert_called_with(service, 'getAllObjects')

    def test_get_location(self):
        id1 = self.lb_mgr._get_location('sjc01')
        self.assertEqual(id1, 168642)

        id2 = self.lb_mgr._get_location('dal05')
        self.assertEqual(id2, 'FIRST_AVAILABLE')

    def test_get_routing_types(self):
        result = self.lb_mgr.get_routing_types()

        self.assertEqual(len(result), 6)
        service = ('SoftLayer_Network_Application_Delivery_Controller_'
                   'LoadBalancer_Routing_Type')
        self.assert_called_with(service, 'getAllObjects')

    def test_cancel_lb(self):
        result = self.lb_mgr.cancel_lb(6327)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelService',
                                identifier=21370814)

    def test_add_local_lb(self):
        self.lb_mgr.add_local_lb(6327, 'sjc01')

        args = ({
            'complexType': 'SoftLayer_Container_Product_Order_Network_'
                           'LoadBalancer',
            'quantity': 1,
            'packageId': 0,
            "location": 168642,
            'prices': [{'id': 6327}]
        },)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder',
                                args=args)

    def test_get_local_lbs(self):
        result = self.lb_mgr.get_local_lbs()

        self.assertEqual(len(result), 0)
        mask = 'mask[loadBalancerHardware[datacenter],ipAddress]'
        self.assert_called_with('SoftLayer_Account', 'getAdcLoadBalancers',
                                mask=mask)

    def test_get_local_lb(self):
        result = self.lb_mgr.get_local_lb(22348)

        self.assertEqual(result['id'], 22348)
        mask = ('mask['
                'loadBalancerHardware[datacenter], '
                'ipAddress, virtualServers[serviceGroups'
                '[routingMethod,routingType,services'
                '[healthChecks[type], groupReferences,'
                ' ipAddress]]]]')
        self.assert_called_with(VIRT_IP_SERVICE, 'getObject',
                                identifier=22348,
                                mask=mask)

    def test_delete_service(self):
        result = self.lb_mgr.delete_service(1234)

        self.assertEqual(result, True)
        service = ('SoftLayer_Network_Application_Delivery_Controller_'
                   'LoadBalancer_Service')
        self.assert_called_with(service, 'deleteObject', identifier=1234)

    def test_delete_service_group(self):
        result = self.lb_mgr.delete_service_group(1234)

        self.assertEqual(result, True)
        service = ('SoftLayer_Network_Application_Delivery_Controller_'
                   'LoadBalancer_VirtualServer')
        self.assert_called_with(service, 'deleteObject', identifier=1234)

    def test_toggle_service_status(self):
        result = self.lb_mgr.toggle_service_status(1234)

        self.assertEqual(result, True)
        service = ('SoftLayer_Network_Application_Delivery_Controller_'
                   'LoadBalancer_Service')
        self.assert_called_with(service, 'toggleStatus', identifier=1234)

    def test_edit_service(self):
        self.lb_mgr.edit_service(12345, 1234, '9.9.9.9', 80, True, 21, 1)

        _filter = {
            'virtualServers': {
                'serviceGroups': {
                    'services': {
                        'id': {
                            'operation': 1234
                        }
                    }
                }
            }
        }
        mask = 'mask[serviceGroups[services[groupReferences,healthChecks]]]'
        self.assert_called_with(VIRT_IP_SERVICE, 'getVirtualServers',
                                identifier=12345,
                                filter=_filter,
                                mask=mask)

        self.assert_called_with(VIRT_IP_SERVICE, 'editObject')

    def test_add_service(self):
        self.lb_mgr.add_service(12345, 50718, 123, 80, True, 21, 1)

        mask = 'mask[virtualServers[serviceGroups[services[groupReferences]]]]'
        self.assert_called_with(VIRT_IP_SERVICE, 'getObject',
                                mask=mask,
                                identifier=12345)

        self.assert_called_with(VIRT_IP_SERVICE, 'editObject',
                                identifier=12345)
        arg = self.calls(VIRT_IP_SERVICE, 'editObject')[0].args[0]
        self.assertEqual(
            len(arg['virtualServers'][0]['serviceGroups'][0]['services']),
            2)

    def test_edit_service_group(self):
        self.lb_mgr.edit_service_group(12345,
                                       group_id=50718,
                                       allocation=100,
                                       port=80,
                                       routing_type=2,
                                       routing_method=10)

        mask = 'mask[virtualServers[serviceGroups[services[groupReferences]]]]'
        self.assert_called_with(VIRT_IP_SERVICE, 'getObject',
                                identifier=12345,
                                mask=mask)

        self.assert_called_with(VIRT_IP_SERVICE, 'getObject', identifier=12345)

    def test_add_service_group(self):
        self.lb_mgr.add_service_group(12345, 100, 80, 2, 10)

        mask = 'mask[virtualServers[serviceGroups[services[groupReferences]]]]'
        self.assert_called_with(VIRT_IP_SERVICE, 'getObject',
                                mask=mask,
                                identifier=12345)

        self.assert_called_with(VIRT_IP_SERVICE, 'editObject',
                                identifier=12345)
        arg = self.calls(VIRT_IP_SERVICE, 'editObject')[0].args[0]
        self.assertEqual(len(arg['virtualServers']), 2)

    def test_reset_service_group(self):
        result = self.lb_mgr.reset_service_group(12345, group_id=50718)

        self.assertEqual(result, True)
        _filter = {'virtualServers': {'id': {'operation': 50718}}}
        self.assert_called_with(VIRT_IP_SERVICE, 'getVirtualServers',
                                identifier=12345,
                                filter=_filter,
                                mask='mask[serviceGroups]')

        service = ('SoftLayer_Network_Application_Delivery_Controller_'
                   'LoadBalancer_Service_Group')
        self.assert_called_with(service, 'kickAllConnections',
                                identifier=51758)
