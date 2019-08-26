"""
    SoftLayer.tests.CLI.modules.loadbal
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :license: MIT, see LICENSE for more details.
"""

import mock

from SoftLayer.CLI.exceptions import ArgumentError
from SoftLayer import exceptions
from SoftLayer.fixtures import SoftLayer_Network_LBaaS_LoadBalancer
from SoftLayer import testing


class LoadBalTests(testing.TestCase):

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
