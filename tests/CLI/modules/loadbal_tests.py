"""
    SoftLayer.tests.managers.loadbal_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from mock import mock

import SoftLayer
from SoftLayer import testing
from SoftLayer.CLI.exceptions import ArgumentError


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
                                   '-b 256', '-c 5'])
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
