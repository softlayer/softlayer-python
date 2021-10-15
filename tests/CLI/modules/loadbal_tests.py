"""
    SoftLayer.tests.CLI.modules.loadbal
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :license: MIT, see LICENSE for more details.
"""
from unittest import mock as mock

import SoftLayer
from SoftLayer.CLI.exceptions import ArgumentError
from SoftLayer import exceptions
from SoftLayer.fixtures import SoftLayer_Network_LBaaS_LoadBalancer
from SoftLayer.fixtures import SoftLayer_Product_Package
from SoftLayer import testing


class LoadBalancerTests(testing.TestCase):

    def test_cli_list(self):
        result = self.run_command(['loadbal', 'list'])
        self.assert_no_fail(result)

    def test_cli_list_failed(self):
        mock_item = self.set_mock('SoftLayer_Network_LBaaS_LoadBalancer',
                                  'getAllObjects')
        mock_item.return_value = None
        result = self.run_command(['loadbal', 'list'])
        self.assert_no_fail(result)

    def test_pool(self):
        result = self.run_command(['loadbal', 'pool-add', '1111111', '-f 1000', '-b 220', '-c 100'])
        self.assert_no_fail(result)

    def test_pool_sticky(self):
        result = self.run_command(['loadbal', 'pool-add', '1111111', '-f 1000', '-b 220', '-s'])
        self.assert_no_fail(result)

    def test_pool_1(self):
        result = self.run_command(['loadbal', 'pool-add', '1111111', '-f 1000', '-b 220'])
        self.assert_no_fail(result)

    def test_pool_uuid(self):
        result = self.run_command(['loadbal', 'pool-add', '13d08cd1-5533-47b4-b71c-4b6b9dc10000',
                                   '-f 910', '-b 210', '-c 100'])
        self.assert_no_fail(result)

    def test_delete_pool(self):
        result = self.run_command(['loadbal', 'pool-del', '111111', 'b3a3fdf7-8c16-4e87-aa73-decff510000'])
        self.assert_no_fail(result)

    def test_edit_pool(self):
        result = self.run_command(['loadbal', 'pool-edit', '111111', '370a9f12-b3be-47b3-bfa5-8e460010000', '-f 510',
                                   '-b 256', '-c 5', '-t 10'])
        self.assert_no_fail(result)

    def test_add_7p(self):
        result = self.run_command(['loadbal', 'l7pool-add', '0a2da082-4474-4e16-9f02-4de959210000', '-n test',
                                   '-S 10.175.106.180:265:20', '-s'])
        self.assert_no_fail(result)

    def test_add_7p_server(self):
        result = self.run_command(['loadbal', 'l7pool-add', '111111',
                                   '-S 10.175.106.180:265:20', '-n test', '-s'])
        self.assert_no_fail(result)

    def test_del_7p(self):
        result = self.run_command(['loadbal', 'l7pool-del', '123456'])
        self.assert_no_fail(result)

    def test_add_7p_server_fail(self):
        result = self.run_command(['loadbal', 'l7pool-add', '123456',
                                   '-S 10.175.106.180:265:20:20', '-n test', '-s'])
        self.assertIsInstance(result.exception, ArgumentError)

    @mock.patch('SoftLayer.LoadBalancerManager.add_lb_listener')
    def test_pool_fail(self, add_lb_pool):
        add_lb_pool.side_effect = SoftLayer.exceptions.SoftLayerAPIError(mock.ANY, mock)
        result = self.run_command(['loadbal', 'pool-add', '123456', '-f 1000', '-b 220', '-c 100'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.LoadBalancerManager.add_lb_listener')
    def test_pool_sticky_fail(self, add_lb_pool):
        add_lb_pool.side_effect = SoftLayer.exceptions.SoftLayerAPIError(mock.ANY, mock)
        result = self.run_command(['loadbal', 'pool-add', '123456', '-f 1000', '-b 220', '-s'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.LoadBalancerManager.add_lb_listener')
    def test_pool_1_fail(self, add_lb_pool):
        add_lb_pool.side_effect = SoftLayer.exceptions.SoftLayerAPIError(mock.ANY, mock)
        result = self.run_command(['loadbal', 'pool-add', '123456', '-f 1000', '-b 220'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.LoadBalancerManager.add_lb_listener')
    def test_pool_uuid_fail(self, add_lb_pool):
        add_lb_pool.side_effect = SoftLayer.exceptions.SoftLayerAPIError(mock.ANY, mock)
        result = self.run_command(
            ['loadbal', 'pool-add', '13d08cd1-5533-47b4-b71c-4b6b9dc10000', '-f 910', '-b 210', '-c 100'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.LoadBalancerManager.remove_lb_listener')
    def test_delete_pool_fail(self, del_lb_pool):
        del_lb_pool.side_effect = SoftLayer.exceptions.SoftLayerAPIError(mock.ANY, mock)
        result = self.run_command(['loadbal', 'pool-del', '123456', 'b3a3fdf7-8c16-4e87-aa73-decff510000'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.LoadBalancerManager.add_lb_listener')
    def test_edit_pool_fail(self, edit_lb_pool):
        edit_lb_pool.side_effect = SoftLayer.exceptions.SoftLayerAPIError(mock.ANY, mock)
        result = self.run_command(['loadbal', 'pool-edit', '815248', '370a9f12-b3be-47b3-bfa5-8e10000c013f', '-f 510',
                                   '-b 256', '-c 5'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.LoadBalancerManager.add_lb_l7_pool')
    def test_add_7p_fail(self, add_lb_17_pool):
        add_lb_17_pool.side_effect = SoftLayer.exceptions.SoftLayerAPIError(mock.ANY, mock)
        result = self.run_command(['loadbal', 'l7pool-add', '0a2da082-4474-4e16-9f02-4de10009b85', '-n test',
                                   '-S 10.175.106.180:265:20', '-s'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.LoadBalancerManager.del_lb_l7_pool')
    def test_del_7p_fail(self, del_lb_17_pool):
        del_lb_17_pool.side_effect = SoftLayer.exceptions.SoftLayerAPIError(mock.ANY, mock)
        result = self.run_command(['loadbal', 'l7pool-del', '123456'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.loadbal.members.click')
    def test_lb_member_add_private(self, click):
        lbaas_id = '1111111'
        member_ip_address = '10.0.0.1'
        result = self.run_command(['loadbal', 'member-add', '--private', '-m', member_ip_address, lbaas_id])
        output = 'Member {} added'.format(member_ip_address)
        self.assert_no_fail(result)
        click.secho.assert_called_with(output, fg='green')

    @mock.patch('SoftLayer.CLI.loadbal.members.click')
    def test_lb_member_add_public(self, click):
        lbaas_id = '1111111'
        member_ip_address = '10.0.0.1'
        result = self.run_command(['loadbal', 'member-add', '--public', '-m', member_ip_address, lbaas_id])
        output = 'Member {} added'.format(member_ip_address)
        self.assert_no_fail(result)
        click.secho.assert_called_with(output, fg='green')

    @mock.patch('SoftLayer.LoadBalancerManager.add_lb_member')
    def test_lb_member_add_public_fails(self, add_lb_member):
        lbaas_id = '1111111'
        member_ip_address = '10.0.0.1'
        fault_string = 'publicIpAddress must be a string'
        add_lb_member.side_effect = exceptions.SoftLayerAPIError(mock.ANY, fault_string)
        result = self.run_command(['loadbal', 'member-add', '--public', '-m', member_ip_address, lbaas_id])
        self.assertIn('This LB requires a Public IP address for its members and none was supplied',
                      result.output)
        self.assertIn("ERROR: {}".format(fault_string),
                      result.output)

    @mock.patch('SoftLayer.LoadBalancerManager.add_lb_member')
    def test_lb_member_add_private_fails(self, add_lb_member):
        lbaas_id = '1111111'
        member_ip_address = '10.0.0.1'
        fault_string = 'privateIpAddress must be a string'
        add_lb_member.side_effect = exceptions.SoftLayerAPIError(mock.ANY, fault_string)
        result = self.run_command(['loadbal', 'member-add', '--private', '-m', member_ip_address, lbaas_id])
        self.assertIn('This LB requires a Private IP address for its members and none was supplied',
                      result.output)
        self.assertIn("ERROR: {}".format(fault_string),
                      result.output)

    @mock.patch('SoftLayer.managers.load_balancer.LoadBalancerManager.delete_lb_member')
    def test_lb_member_del_fails(self, delete):
        lbaas_id = '1111111'
        lbaas_member_uuid = "x123x123-123x-123x-123x-123a123b123c"
        delete.side_effect = exceptions.SoftLayerAPIError(mock.ANY, mock.ANY)
        result = self.run_command(['loadbal', 'member-del', '-m', lbaas_member_uuid, lbaas_id])
        self.assertIn("ERROR:", result.output)

    @mock.patch('SoftLayer.CLI.loadbal.members.click')
    def test_lb_member_del(self, click):
        lbaas_id = '1111111'
        lbaas_member_uuid = "x123x123-123x-123x-123x-123a123b123c"
        result = self.run_command(['loadbal', 'member-del', '-m', lbaas_member_uuid, lbaas_id])
        output = 'Member {} removed'.format(lbaas_member_uuid)
        self.assert_no_fail(result)
        click.secho.assert_called_with(output, fg='green')

    def test_lb_l7policies_list(self):
        command = 'loadbal l7policies'
        result = self.run_command(command.split(' '))
        self.assert_no_fail(result)

    def test_lb_l7policies_protocol_list(self):
        command = 'loadbal l7policies -p 123456'
        result = self.run_command(command.split(' '))
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.loadbal.health.click')
    def test_lb_health_manage(self, click):
        lb_id = '1111111'
        lb_check_uuid = '222222ab-bbcc-4f32-9b31-1b6d3a1959c8'
        result = self.run_command(['loadbal', 'health', lb_id, '--uuid', lb_check_uuid,
                                   '-i', '60', '-r', '10', '-t', '10', '-u', '/'])
        self.assert_no_fail(result)
        output = 'Health Check {} updated successfully'.format(lb_check_uuid)
        click.secho.assert_called_with(output, fg='green')

    def test_lb_health_manage_args_time_fails(self):
        result = self.run_command(['lb', 'health', '1111111', '--uuid', '222222ab-bbcc-4f32-9b31-1b6d3a1959c8'])
        self.assertIsInstance(result.exception, ArgumentError)

    @mock.patch('SoftLayer.LoadBalancerManager.get_lb')
    def test_lb_health_update_tcp_url_fails(self, get_lb):
        get_lb.return_value = SoftLayer_Network_LBaaS_LoadBalancer.getObject
        get_lb.return_value['listeners'][0]['defaultPool']['protocol'] = 'TCP'

        result = self.run_command(['lb', 'health', '1111111', '--uuid', '222222ab-bbcc-4f32-9b31-1b6d3a1959c8',
                                   '-i', '60', '-r', '10', '-t', '10', '-u', '/'])
        self.assertIsInstance(result.exception, ArgumentError)

    @mock.patch('SoftLayer.LoadBalancerManager.update_lb_health_monitors')
    def test_lb_health_update_fails(self, update_lb_health_monitors):
        update_lb_health_monitors.side_effect = exceptions.SoftLayerAPIError(mock.ANY, mock.ANY)

        result = self.run_command(['lb', 'health', '1111111', '--uuid', '222222ab-bbcc-4f32-9b31-1b6d3a1959c8',
                                   '-i', '60', '-r', '10', '-t', '10', '-u', '/'])
        self.assertIn("ERROR:", result.output)

    def test_lb_detail(self):
        result = self.run_command(['lb', 'detail', '1111111'])
        self.assert_no_fail(result)
        self.assertIn('Id', result.output)
        self.assertIn('UUI', result.output)
        self.assertIn('Address', result.output)

    def test_lb_detail_by_name(self):
        name = SoftLayer_Network_LBaaS_LoadBalancer.getObject.get('name')
        result = self.run_command(['lb', 'detail', name])
        self.assert_no_fail(result)

    def test_lb_detail_uuid(self):
        uuid = SoftLayer_Network_LBaaS_LoadBalancer.getObject.get('uuid')
        result = self.run_command(['lb', 'detail', uuid])
        self.assert_no_fail(result)

    def test_order(self):
        result = self.run_command(['loadbal', 'order', '--name', 'test', '--datacenter', 'par01', '--label',
                                   'labeltest', '--subnet', '759282'])

        self.assert_no_fail(result)

    def test_order_with_frontend(self):
        result = self.run_command(['loadbal', 'order', '--name', 'test', '--datacenter', 'par01', '--label',
                                   'labeltest', '--frontend', 'TCP:80', '--backend', 'TCP:80', '--subnet', '759282'])

        self.assert_no_fail(result)

    def test_order_with_backend(self):
        result = self.run_command(['loadbal', 'order', '--name', 'test', '--datacenter', 'par01', '--label',
                                   'labeltest', '--backend', 'HTTP:80', '--subnet', '759282'])

        self.assert_no_fail(result)

    def test_order_backend_fail(self):
        result = self.run_command(['loadbal', 'order', '--name', 'test', '--datacenter', 'par01', '--label',
                                   'labeltest', '--backend', 'HTTP', '--subnet', '759282'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, ArgumentError)

    def test_verify_order(self):
        result = self.run_command(['loadbal', 'order', '--verify', '--name', 'test', '--datacenter', 'par01', '--label',
                                   'labeltest', '--subnet', '759282'])

        self.assert_no_fail(result)

    def test_order_options(self):
        fault_string = 'Use `slcli lb order-options --datacenter <DC>`' \
                       ' to find pricing information and private subnets for that specific site.'
        result = self.run_command(['loadbal', 'order-options'])
        self.assertIn(fault_string, result.output)

    def test_order_options_with_datacenter(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = SoftLayer_Product_Package.getAllObjectsLoadbal
        result = self.run_command(['loadbal', 'order-options', '--datacenter', 'ams03'])

        self.assert_no_fail(result)

    def test_cancel(self):
        result = self.run_command(['loadbal', 'cancel', '11111'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_LBaaS_LoadBalancer', 'cancelLoadBalancer')

    @mock.patch('SoftLayer.LoadBalancerManager.cancel_lbaas')
    def test_cancel_fail(self, cancel_lbaas):
        fault_string = 'Id must be string'
        cancel_lbaas.side_effect = exceptions.SoftLayerAPIError(mock.ANY, fault_string)
        result = self.run_command(['loadbal', 'cancel', '11111'])

        self.assertIn("ERROR: {}".format(fault_string),
                      result.output)

    def test_ns_list(self):
        result = self.run_command(['loadbal', 'ns-list'])

        self.assert_no_fail(result)

    def test_ns_list_empty(self):
        mock = self.set_mock('SoftLayer_Account', 'getApplicationDeliveryControllers')
        mock.return_value = []

        result = self.run_command(['loadbal', 'ns-list'])

        self.assert_no_fail(result)

    def test_ns_detail(self):
        result = self.run_command(['loadbal', 'ns-detail', '11111'])

        self.assert_no_fail(result)
