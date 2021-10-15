"""
    SoftLayer.tests.managers.loadbal_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.

    A lot of these tests will use junk data because the manager just passes
    them directly to the API.
"""
import SoftLayer
from SoftLayer import exceptions
from SoftLayer.fixtures import SoftLayer_Network_LBaaS_LoadBalancer
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

    def test_updated_lb_health(self):
        uuid = '1234'
        check = {'backendPort': '80'}
        self.lb_mgr.update_lb_health_monitors(uuid, check)
        self.assert_called_with('SoftLayer_Network_LBaaS_HealthMonitor', 'updateLoadBalancerHealthMonitors',
                                args=(uuid, check))

    def test_get_lbaas_uuid_id_uuid(self):
        uuid = '1a1aa111-4474-4e16-9f02-4de959229b85'
        my_id = 1111111
        lb_uuid, lb_id = self.lb_mgr.get_lbaas_uuid_id(uuid)
        self.assert_called_with('SoftLayer_Network_LBaaS_LoadBalancer', 'getLoadBalancer', args=(uuid,))
        self.assertEqual(lb_uuid, uuid)
        self.assertEqual(lb_id, my_id)

    def test_get_lbaas_uuid_id_id(self):
        uuid = '1a1aa111-4474-4e16-9f02-4de959229b85'
        my_id = 1111111
        lb_uuid, lb_id = self.lb_mgr.get_lbaas_uuid_id(my_id)
        self.assert_called_with('SoftLayer_Network_LBaaS_LoadBalancer', 'getObject', identifier=my_id)
        self.assertEqual(lb_uuid, uuid)
        self.assertEqual(lb_id, my_id)

    def test_get_lbaas_uuid_id_name(self):
        uuid = '1a1aa111-4474-4e16-9f02-4de959229b85'
        my_id = 1111111
        name = 'test-01'
        lb_uuid, lb_id = self.lb_mgr.get_lbaas_uuid_id(name)
        self.assert_called_with('SoftLayer_Network_LBaaS_LoadBalancer', 'getAllObjects')
        self.assertEqual(lb_uuid, uuid)
        self.assertEqual(lb_id, my_id)

    def test_delete_lb_member(self):
        uuid = 'aa-bb-cc'
        member_id = 'dd-ee-ff'
        self.lb_mgr.delete_lb_member(uuid, member_id)
        self.assert_called_with('SoftLayer_Network_LBaaS_Member', 'deleteLoadBalancerMembers',
                                args=(uuid, [member_id]))

    def test_add_lb_member(self):
        uuid = 'aa-bb-cc'
        member = {'privateIpAddress': '1.2.3.4'}
        self.lb_mgr.add_lb_member(uuid, member)
        self.assert_called_with('SoftLayer_Network_LBaaS_Member', 'addLoadBalancerMembers',
                                args=(uuid, [member]))

    def test_add_lb_listener(self):
        uuid = 'aa-bb-cc'
        listener = {'id': 1}
        self.lb_mgr.add_lb_listener(uuid, listener)
        self.assert_called_with('SoftLayer_Network_LBaaS_Listener', 'updateLoadBalancerProtocols',
                                args=(uuid, [listener]))

    def test_get_l7policies(self):
        my_id = 1111111
        self.lb_mgr.get_l7policies(my_id)
        self.assert_called_with('SoftLayer_Network_LBaaS_Listener', 'getL7Policies', identifier=my_id)

    def test_get_all_l7policies(self):
        policies = self.lb_mgr.get_all_l7policies()
        self.assert_called_with('SoftLayer_Network_LBaaS_LoadBalancer', 'getAllObjects')
        self.assertIsInstance(policies, dict)

    def test_add_lb_l7_pool(self):
        uuid = 'aa-bb-cc'
        pool = {'id': 1}
        members = {'id': 1}
        health = {'id': 1}
        session = {'id': 1}
        self.lb_mgr.add_lb_l7_pool(uuid, pool, members, health, session)
        self.assert_called_with('SoftLayer_Network_LBaaS_L7Pool', 'createL7Pool',
                                args=(uuid, pool, members, health, session))

    def test_del_lb_l7_pool(self):
        uuid = 'aa-bb-cc'
        self.lb_mgr.del_lb_l7_pool(uuid)
        self.assert_called_with('SoftLayer_Network_LBaaS_L7Pool', 'deleteObject', identifier=uuid)

    def test_remove_lb_listener(self):
        uuid = 'aa-bb-cc'
        listener = 'dd-ee-ff'
        self.lb_mgr.remove_lb_listener(uuid, listener)
        self.assert_called_with('SoftLayer_Network_LBaaS_Listener', 'deleteLoadBalancerProtocols',
                                args=(uuid, [listener]))

    def test_order_lbaas(self):
        datacenter = 'tes01'
        name = 'test-lb'
        desc = 'my lb'
        protocols = {'frontendPort': 80, 'frontendProtocol': 'HTTP'}
        subnet_id = 12345
        public = True
        verify = False
        package = [
            {
                'id': 805,
                'keyNake': 'LBAAS',
                'itemPrices': [
                    {
                        'id': 1,
                        'name': 'A test price',
                        'locationGroupId': None
                    },
                    {
                        'id': 2,
                        'name': 'A test price 2',
                        'locationGroupId': 123
                    }
                ]
            }
        ]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = package
        order_data = {
            'complexType': 'SoftLayer_Container_Product_Order_Network_LoadBalancer_AsAService',
            'name': name,
            'description': desc,
            'location': datacenter,
            'packageId': package[0]['id'],
            'useHourlyPricing': True,  # Required since LBaaS is an hourly service
            'prices': [{'id': package[0]['itemPrices'][0]['id']}],
            'protocolConfigurations': protocols,
            'subnets': [{'id': subnet_id}],
            'isPublic': public
        }
        self.lb_mgr.order_lbaas(datacenter, name, desc, protocols, subnet_id, public, verify)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder', args=(order_data,))
        self.assert_called_with('SoftLayer_Product_Package', 'getAllObjects')
        verify = True
        self.lb_mgr.order_lbaas(datacenter, name, desc, protocols, subnet_id, public, verify)
        self.assert_called_with('SoftLayer_Product_Order', 'verifyOrder')

    def test_lbaas_order_options(self):
        self.lb_mgr.lbaas_order_options()
        self.assert_called_with('SoftLayer_Product_Package', 'getAllObjects')

    def test_cancel_lbaas(self):
        uuid = 'aa-bb-cc'
        self.lb_mgr.cancel_lbaas(uuid)
        self.assert_called_with('SoftLayer_Network_LBaaS_LoadBalancer', 'cancelLoadBalancer', args=(uuid,))

    def test_get_lbaas_by_name(self):
        name = SoftLayer_Network_LBaaS_LoadBalancer.getObject.get('name')
        load_bal = self.lb_mgr.get_lbaas_by_name(name)
        self.assert_called_with('SoftLayer_Network_LBaaS_LoadBalancer', 'getAllObjects')
        self.assertIsNotNone(load_bal)

    def test_get_lbaas_by_name_fails(self):
        load_bal_mock = self.set_mock('SoftLayer_Network_LBaaS_LoadBalancer', 'getAllObjects')
        load_bal_mock.return_value = []
        name = 'test'
        self.assertRaises(exceptions.SoftLayerError, self.lb_mgr.get_lbaas_by_name, name)
