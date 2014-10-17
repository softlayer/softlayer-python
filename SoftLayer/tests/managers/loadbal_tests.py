"""
    SoftLayer.tests.managers.loadbal_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import testing
from SoftLayer.testing import fixtures


class LoadBalancerTests(testing.TestCase):

    def set_up(self):
        self.client = testing.FixtureClient()
        self.lb_mgr = SoftLayer.LoadBalancerManager(self.client)

    def test_get_lb_pkgs(self):
        self.lb_mgr.get_lb_pkgs()
        f = self.client['Product_Package'].getItems
        _filter = {
            'items': {
                'description': {
                    'operation': '*= Load Balancer'
                }
            }
        }
        f.assert_called_once_with(filter=_filter, id=0)

    def test_get_hc_types(self):
        self.lb_mgr.get_hc_types()
        f = self.client['Network_Application_Delivery_Controller_'
                        'LoadBalancer_Health_Check_Type'].getAllObjects
        f.assert_called_once()

    def test_get_routing_methods(self):
        self.lb_mgr.get_routing_methods()
        f = self.client['Network_Application_Delivery_Controller_'
                        'LoadBalancer_Routing_Method'].getAllObjects
        f.assert_called_once()

    def test_get_location(self):
        id1 = self.lb_mgr.get_location('sjc01')
        f = self.client['Location'].getDataCenters
        f.assert_called_once()
        self.assertEqual(id1, 168642)

        id2 = self.lb_mgr.get_location('dal05')
        f = self.client['Location'].getDataCenters
        f.assert_called_once()
        self.assertEqual(id2, 'FIRST_AVAILABLE')

    def test_get_routing_types(self):
        self.lb_mgr.get_routing_types()
        f = self.client['Network_Application_Delivery_Controller_'
                        'LoadBalancer_Routing_Type'].getAllObjects
        f.assert_called_once()

    def test_cancel_lb(self):
        loadbal_id = 6327
        billing_item_id = 21370814
        result = self.lb_mgr.cancel_lb(loadbal_id)
        f = self.client['Billing_Item'].cancelService
        f.assert_called_once_with(id=billing_item_id)
        self.assertEqual(result, fixtures.Billing_Item.cancelService)

    def test_add_local_lb(self):
        price_id = 6327
        datacenter = 'sjc01'
        self.lb_mgr.add_local_lb(price_id, datacenter)

        _package = {
            'complexType': 'SoftLayer_Container_Product_Order_Network_'
                           'LoadBalancer',
            'quantity': 1,
            'packageId': 0,
            "location": 168642,
            'prices': [{'id': price_id}]
        }
        f = self.client['Product_Order'].placeOrder
        f.assert_called_once_with(_package)

    def test_get_local_lbs(self):
        self.lb_mgr.get_local_lbs()
        call = self.client['Account'].getAdcLoadBalancers
        mask = ('mask[loadBalancerHardware[datacenter],ipAddress]')
        call.assert_called_once_with(mask=mask)

    def test_get_local_lb(self):
        lb_id = 12345
        self.lb_mgr.get_local_lb(lb_id)
        call = self.client['Network_Application_Delivery_Controller_'
                           'LoadBalancer_VirtualIpAddress'].getObject

        mask = ('mask[loadBalancerHardware[datacenter], '
                'ipAddress, virtualServers[serviceGroups'
                '[routingMethod,routingType,services'
                '[healthChecks[type], groupReferences,'
                ' ipAddress]]]]')
        call.assert_called_once_with(id=lb_id, mask=mask)

    def test_delete_service(self):
        service_id = 1234
        self.lb_mgr.delete_service(service_id)
        call = self.client['Network_Application_Delivery_Controller_'
                           'LoadBalancer_Service'].deleteObject

        call.assert_called_once_with(id=service_id)

    def test_delete_service_group(self):
        service_group = 1234
        self.lb_mgr.delete_service_group(service_group)
        call = self.client['Network_Application_Delivery_Controller_'
                           'LoadBalancer_VirtualServer'].deleteObject

        call.assert_called_once_with(id=service_group)

    def test_toggle_service_status(self):
        service_id = 1234
        self.lb_mgr.toggle_service_status(service_id)
        call = self.client['Network_Application_Delivery_Controller_'
                           'LoadBalancer_Service'].toggleStatus

        call.assert_called_once_with(id=service_id)

    def test_edit_service(self):
        loadbal_id = 12345
        service_id = 1234
        ip_address = '9.9.9.9'
        port = 80
        enabled = 1
        hc_type = 21
        weight = 1
        self.lb_mgr.edit_service(loadbal_id, service_id, ip_address,
                                 port, enabled, hc_type, weight)
        call = self.client['Network_Application_Delivery_Controller_'
                           'LoadBalancer_VirtualIpAddress'].getVirtualServers
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
        call.assert_called_once_with(filter=_filter, mask=mask, id=loadbal_id)

        call = self.client['Network_Application_Delivery_Controller_'
                           'LoadBalancer_VirtualIpAddress'].editObject
        call.assert_called_once()

    def test_add_service(self):
        loadbal_id = 12345
        group_id = 50718
        ip_address_id = 123
        port = 80
        enabled = 1
        hc_type = 21
        weight = 1
        self.lb_mgr.add_service(loadbal_id, group_id, ip_address_id,
                                port, enabled, hc_type, weight)
        call = self.client['Network_Application_Delivery_Controller_'
                           'LoadBalancer_VirtualIpAddress'].getObject

        mask = ('mask[virtualServers[serviceGroups'
                '[services[groupReferences]]]]')
        call.assert_called_once_with(mask=mask, id=loadbal_id)

        call = self.client['Network_Application_Delivery_Controller_'
                           'LoadBalancer_VirtualIpAddress'].editObject
        call.assert_called_once()

    def test_edit_service_group(self):
        loadbal_id = 12345
        group_id = 50718
        allocation = 100
        port = 80
        routing_type = 2
        routing_method = 10
        self.lb_mgr.edit_service_group(loadbal_id, group_id=group_id,
                                       allocation=allocation,
                                       port=port,
                                       routing_type=routing_type,
                                       routing_method=routing_method)
        call = self.client['Network_Application_Delivery_Controller_'
                           'LoadBalancer_VirtualIpAddress'].getObject

        mask = ('mask[virtualServers[serviceGroups'
                '[services[groupReferences]]]]')
        call.assert_called_once_with(mask=mask, id=loadbal_id)

        call = self.client['Network_Application_Delivery_Controller_'
                           'LoadBalancer_VirtualIpAddress'].editObject
        call.assert_called_once()

    def test_add_service_group(self):
        loadbal_id = 12345
        allocation = 100
        port = 80
        routing_type = 2
        routing_method = 10
        self.lb_mgr.add_service_group(loadbal_id, allocation, port,
                                      routing_type, routing_method)
        call = self.client['Network_Application_Delivery_Controller_'
                           'LoadBalancer_VirtualIpAddress'].getObject

        mask = ('mask[virtualServers[serviceGroups'
                '[services[groupReferences]]]]')
        call.assert_called_once_with(mask=mask, id=loadbal_id)

        call = self.client['Network_Application_Delivery_Controller_'
                           'LoadBalancer_VirtualIpAddress'].editObject
        call.assert_called_once()

    def test_reset_service_group(self):
        loadbal_id = 12345
        group_id = 50718
        self.lb_mgr.reset_service_group(loadbal_id, group_id=group_id)
        call = self.client['Network_Application_Delivery_Controller_'
                           'LoadBalancer_VirtualIpAddress'].getVirtualServers

        _filter = {'virtualServers': {'id': {'operation': group_id}}}
        mask = 'mask[serviceGroups]'
        call.assert_called_once_with(filter=_filter, mask=mask, id=loadbal_id)

        call = self.client['Network_Application_Delivery_Controller_'
                           'LoadBalancer_Service_Group'].kickAllConnections
        call.assert_called_once_with(id=51758)
