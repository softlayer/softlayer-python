"""
    SoftLayer.tests.CLI.modules.hardware.hardware_list_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    These tests the `slcli hw list` command. Its complex enough to warrant its own file

    :license: MIT, see LICENSE for more details.
"""

import json

from SoftLayer import testing
from SoftLayer import utils


class HardwareListCLITests(testing.TestCase):
    def test_list_servers(self):
        colums = 'datacenter,primary_ip,hostname,id,backend_ip,action'
        result = self.run_command(['server', 'list', '--tag=openstack', f'--columns={colums}'])

        expected = [
            {
                'datacenter': 'TEST00',
                'primary_ip': '172.16.1.100',
                'hostname': 'hardware-test1',
                'id': 1000,
                'backend_ip': '10.1.0.2',
                'action': 'TXN_NAME',
            },
            {
                'datacenter': 'TEST00',
                'primary_ip': '172.16.4.94',
                'hostname': 'hardware-test2',
                'id': 1001,
                'backend_ip': '10.1.0.3',
                'action': None,
            },
            {
                'datacenter': 'TEST00',
                'primary_ip': '172.16.4.95',
                'hostname': 'hardware-bad-memory',
                'id': 1002,
                'backend_ip': '10.1.0.4',
                'action': None,
            },
            {
                'action': None,
                'backend_ip': None,
                'datacenter': None,
                'hostname': None,
                'id': 1003,
                'primary_ip': None,
            },
        ]

        self.assert_no_fail(result)
        self.assertEqual(expected, json.loads(result.output))

    def test_list_hw_search_noargs(self):
        result = self.run_command(['hw', 'list', '--search'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Search', 'advancedSearch', args=('_objectType:SoftLayer_Hardware ',))

    def test_list_hw_search_noargs_domain(self):
        result = self.run_command(['hw', 'list', '--search', '-Dtest'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Search', 'advancedSearch',
                                args=('_objectType:SoftLayer_Hardware  domain: *test*',))

    def test_list_by_owner(self):
        result = self.run_command(['hw', 'list', '--owner=testUser'])
        self.assert_no_fail(result)
        expectedFilter = utils.NestedDict()
        expectedFilter['id'] = utils.query_filter_orderby()
        expectedFilter['hardware']['billingItem']['orderItem']['order']['userRecord']['username'] = (
                utils.query_filter('testUser'))
        self.assert_called_with('SoftLayer_Account', 'getHardware', filter=expectedFilter)

    def test_list_by_pub_ip(self):
        result = self.run_command(['hw', 'list', '--primary_ip=1.2.3.4'])
        self.assert_no_fail(result)
        expectedFilter = utils.NestedDict()
        expectedFilter['id'] = utils.query_filter_orderby()
        expectedFilter['hardware']['primaryIpAddress'] = utils.query_filter('1.2.3.4')
        self.assert_called_with('SoftLayer_Account', 'getHardware', filter=expectedFilter)

    def test_list_by_pri_ip(self):
        result = self.run_command(['hw', 'list', '--backend_ip=1.2.3.4'])
        self.assert_no_fail(result)
        expectedFilter = utils.NestedDict()
        expectedFilter['id'] = utils.query_filter_orderby()
        expectedFilter['hardware']['primaryBackendIpAddress'] = utils.query_filter('1.2.3.4')
        self.assert_called_with('SoftLayer_Account', 'getHardware', filter=expectedFilter)
