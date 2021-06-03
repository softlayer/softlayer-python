"""
    SoftLayer.tests.CLI.modules.server_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This is a series of integration tests designed to test the complete
    command line interface.

    :license: MIT, see LICENSE for more details.
"""

import json
import sys
import tempfile
from unittest import mock as mock

from SoftLayer.CLI import exceptions
from SoftLayer.fixtures import SoftLayer_Product_Order
from SoftLayer import SoftLayerError
from SoftLayer import testing


class ServerCLITests(testing.TestCase):

    def test_server_cancel_reasons(self):
        result = self.run_command(['server', 'cancel-reasons'])
        output = json.loads(result.output)
        self.assert_no_fail(result)
        self.assertEqual(len(output), 10)

    def test_server_credentials(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {
            "accountId": 11111,
            "domain": "chechu.com",
            "fullyQualifiedDomainName": "host3.vmware.chechu.com",
            "hardwareStatusId": 5,
            "hostname": "host3.vmware",
            "id": 12345,
            "softwareComponents": [{"passwords": [
                {
                    "password": "abc123",
                    "username": "root"
                }
            ]}]
        }
        result = self.run_command(['hardware', 'credentials', '12345'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{
                             'username': 'root',
                             'password': 'abc123'
                         }])

    def test_server_credentials_exception_passwords_not_found(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {
            "accountId": 11111,
            "domain": "chechu.com",
            "fullyQualifiedDomainName": "host3.vmware.chechu.com",
            "hardwareStatusId": 5,
            "hostname": "host3.vmware",
            "id": 12345,
            "softwareComponents": [{}]
        }

        result = self.run_command(['hardware', 'credentials', '12345'])

        self.assertEqual(
            'No passwords found in softwareComponents',
            str(result.exception)
        )

    def test_server_credentials_exception_password_not_found(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {
            "accountId": 11111,
            "domain": "chechu.com",
            "fullyQualifiedDomainName": "host3.vmware.chechu.com",
            "hardwareStatusId": 5,
            "hostname": "host3.vmware",
            "id": 12345,
            "softwareComponents": [
                {
                    "hardwareId": 22222,
                    "id": 333333,
                    "passwords": [{}]
                }
            ]
        }

        result = self.run_command(['hardware', 'credentials', '12345'])

        self.assertEqual(
            'None',
            str(result.exception)
        )

    def test_server_details(self):
        result = self.run_command(['server', 'detail', '1234', '--passwords', '--price'])

        self.assert_no_fail(result)
        output = json.loads(result.output)
        self.assertEqual(output['notes'], 'These are test notes.')
        self.assertEqual(output['prices'][0]['Recurring Price'], 16.08)
        self.assertEqual(output['remote users'][0]['password'], 'abc123')
        self.assertEqual(output['users'][0]['username'], 'root')
        self.assertEqual(output['vlans'][0]['number'], 1800)
        self.assertEqual(output['owner'], 'chechu')
        self.assertEqual(output['Bandwidth'][0]['Allotment'], '250')

    def test_detail_vs_empty_tag(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {
            'id': 100,
            'processorPhysicalCoreAmount': 2,
            'memoryCapacity': 2,
            'tagReferences': [
                {'tag': {'name': 'example-tag'}},
                {},
            ],
        }
        result = self.run_command(['server', 'detail', '100'])

        self.assert_no_fail(result)
        self.assertEqual(
            json.loads(result.output)['tags'],
            ['example-tag'],
        )

    def test_detail_empty_allotment(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getBandwidthAllotmentDetail')
        mock.return_value = None
        result = self.run_command(['server', 'detail', '100'])

        self.assert_no_fail(result)
        self.assertEqual(
            json.loads(result.output)['Bandwidth'][0]['Allotment'],
            '-',
        )

    def test_detail_drives(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getHardDrives')
        mock.return_value = [
            {
                "id": 11111,
                "serialNumber": "z1w4sdf",
                "hardwareComponentModel": {
                    "capacity": "1000",
                    "description": "SATAIII:2000:8300:Constellation",
                    "id": 111,
                    "manufacturer": "Seagate",
                    "name": "Constellation ES",
                    "hardwareGenericComponentModel": {
                        "capacity": "1000",
                        "units": "GB",
                        "hardwareComponentType": {
                            "id": 1,
                            "keyName": "HARD_DRIVE",
                            "type": "Hard Drive",
                            "typeParentId": 5
                        }
                    }
                }
            }
        ]
        result = self.run_command(['server', 'detail', '100'])

        self.assert_no_fail(result)
        output = json.loads(result.output)
        self.assertEqual(output['drives'][0]['Capacity'], '1000 GB')
        self.assertEqual(output['drives'][0]['Name'], 'Seagate Constellation ES')
        self.assertEqual(output['drives'][0]['Serial #'], 'z1w4sdf')

    def test_list_servers(self):
        result = self.run_command(['server', 'list', '--tag=openstack'])

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

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    @mock.patch('SoftLayer.HardwareManager.reload')
    def test_server_reload(self, reload_mock, ngb_mock):
        ngb_mock.return_value = False

        # Check the positive case
        result = self.run_command(['--really', 'server', 'reload', '12345', '--key=4567'])

        self.assert_no_fail(result)
        reload_mock.assert_called_with(12345, None, [4567], False)

        # LVM switch
        result = self.run_command(['--really', 'server', 'reload', '12345', '--lvm'])
        self.assert_no_fail(result)
        reload_mock.assert_called_with(12345, None, [], True)

        # Now check to make sure we properly call CLIAbort in the negative case
        result = self.run_command(['server', 'reload', '12345'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    @mock.patch('SoftLayer.HardwareManager.cancel_hardware')
    def test_cancel_server(self, cancel_mock, ngb_mock):
        ngb_mock.return_value = False

        # Check the positive case
        result = self.run_command(['--really', 'server', 'cancel', '12345',
                                   '--reason=Test', '--comment=Test'])

        self.assert_no_fail(result)
        cancel_mock.assert_called_with(12345, "Test", "Test", False)

        # Test
        result = self.run_command(['server', 'cancel', '12345',
                                   '--reason=Test', '--comment=Test'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_server_power_off(self, confirm_mock):
        # Check the positive case
        result = self.run_command(['--really', 'server', 'power-off', '12345'])

        self.assert_called_with('SoftLayer_Hardware_Server', 'powerOff',
                                identifier=12345)

        # Now check to make sure we properly call CLIAbort in the negative case
        confirm_mock.return_value = False
        result = self.run_command(['server', 'power-off', '12345'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_server_reboot_default(self):
        result = self.run_command(['--really', 'server', 'reboot', '12345'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Hardware_Server', 'rebootDefault',
                                identifier=12345)

    def test_server_reboot_soft(self):
        result = self.run_command(['--really', 'server', 'reboot', '12345',
                                   '--soft'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Hardware_Server', 'rebootSoft',
                                identifier=12345)

    def test_server_reboot_hard(self):
        result = self.run_command(['--really', 'server', 'reboot', '12345',
                                   '--hard'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Hardware_Server', 'rebootHard',
                                identifier=12345)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_server_reboot_negative(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['server', 'reboot', '12345'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_server_power_on(self):
        result = self.run_command(['--really', 'server', 'power-on', '12345'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Hardware_Server', 'powerOn',
                                identifier=12345)

    def test_server_power_cycle(self):
        result = self.run_command(['--really', 'server', 'power-cycle',
                                   '12345'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Hardware_Server', 'powerCycle',
                                identifier=12345)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_server_power_cycle_negative(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['server', 'power-cycle', '12345'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('SoftLayer.HardwareManager.verify_order')
    def test_create_server_test_flag(self, verify_mock):
        verify_mock.return_value = {
            'prices': [
                {
                    'recurringFee': 0.0,
                    'setupFee': 0.0,
                    'item': {'description': 'First Item'},
                },
                {
                    'recurringFee': 25.0,
                    'setupFee': 0.0,
                    'item': {'description': 'Second Item'},
                }
            ]
        }

        result = self.run_command(['--really', 'server', 'create',
                                   '--size=S1270_8GB_2X1TBSATA_NORAID',
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--port-speed=100',
                                   '--os=UBUNTU_12_64',
                                   '--test'],
                                  fmt='raw')

        self.assert_no_fail(result)
        self.assertIn("First Item", result.output)
        self.assertIn("Second Item", result.output)
        self.assertIn("Total monthly cost", result.output)

    def test_create_options(self):
        result = self.run_command(['server', 'create-options'])

        self.assert_no_fail(result)
        output = json.loads(result.output)
        self.assertEqual(output[0][0]['Value'], 'wdc07')

    def test_create_options_prices(self):
        result = self.run_command(['server', 'create-options', '--prices'])

        self.assert_no_fail(result)
        output = json.loads(result.output)
        self.assertEqual(output[2][0]['Monthly'], str(0.1))
        self.assertEqual(output[2][0]['Key'], 'OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT')

    def test_create_options_location(self):
        result = self.run_command(['server', 'create-options', '--prices', 'dal13'])

        self.assert_no_fail(result)
        output = json.loads(result.output)
        self.assertEqual(output[2][0]['Monthly'], str(0.1))
        self.assertEqual(output[2][0]['Key'], 'OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT')

    @mock.patch('SoftLayer.HardwareManager.place_order')
    def test_create_server(self, order_mock):
        order_mock.return_value = {
            'orderId': 98765,
            'orderDate': '2013-08-02 15:23:47'
        }

        result = self.run_command(['--really', 'server', 'create',
                                   '--size=S1270_8GB_2X1TBSATA_NORAID',
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--port-speed=100',
                                   '--os=OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT',
                                   '--no-public',
                                   '--key=10',
                                   ])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         {'id': 98765, 'created': '2013-08-02 15:23:47'})

    @mock.patch('SoftLayer.CLI.template.export_to_template')
    def test_create_server_with_export(self, export_mock):

        result = self.run_command(['--really', 'server', 'create',
                                   '--size=S1270_8GB_2X1TBSATA_NORAID',
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--port-speed=100',
                                   '--os=UBUNTU_12_64',
                                   '--no-public',
                                   '--export=/path/to/test_file.txt'],
                                  fmt='raw')

        self.assert_no_fail(result)
        self.assertIn("Successfully exported options to a template file.", result.output)
        export_mock.assert_called_once()

    @mock.patch('SoftLayer.HardwareManager.place_order')
    def test_create_server_with_router(self, order_mock):
        order_mock.return_value = {
            'orderId': 98765,
            'orderDate': '2013-08-02 15:23:47'
        }

        result = self.run_command(['--really', 'server', 'create',
                                   '--size=S1270_8GB_2X1TBSATA_NORAID',
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--port-speed=100',
                                   '--os=OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT',
                                   '--router-private=123',
                                   '--router-public=1234'
                                   ])

        self.assert_no_fail(result)

    def test_edit_server_userdata_and_file(self):
        # Test both userdata and userfile at once
        with tempfile.NamedTemporaryFile() as userfile:
            result = self.run_command(['server', 'edit', '1000',
                                       '--hostname=hardware-test1',
                                       '--domain=test.sftlyr.ws',
                                       '--userdata=My data',
                                       '--userfile=%s' % userfile.name])

            self.assertEqual(result.exit_code, 2)
            self.assertIsInstance(result.exception, exceptions.ArgumentError)

    def test_edit_server_userdata(self):
        result = self.run_command(['server', 'edit', '1000',
                                   '--hostname=hardware-test1',
                                   '--domain=test.sftlyr.ws',
                                   '--userdata=My data'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")
        self.assert_called_with('SoftLayer_Hardware_Server', 'editObject',
                                args=({'domain': 'test.sftlyr.ws',
                                       'hostname': 'hardware-test1'},),
                                identifier=1000)

    @mock.patch('SoftLayer.HardwareManager.edit')
    def test_edit_server_failed(self, edit_mock):
        edit_mock.return_value = False
        result = self.run_command(['server', 'edit', '1000',
                                   '--hostname=hardware-test1',
                                   '--domain=test.sftlyr.ws',
                                   '--userdata=My data'])

        self.assertEqual(result.exit_code, 2)
        self.assertEqual(result.output, "")
        edit_mock.assert_called_with(1000,
                                     userdata='My data',
                                     domain='test.sftlyr.ws',
                                     hostname='hardware-test1')

    def test_edit_server_userfile(self):
        if (sys.platform.startswith("win")):
            self.skipTest("Test doesn't work in Windows")
        with tempfile.NamedTemporaryFile() as userfile:
            userfile.write(b"some data")
            userfile.flush()
            result = self.run_command(['server', 'edit', '1000',
                                       '--userfile=%s' % userfile.name])

            self.assert_no_fail(result)
            self.assertEqual(result.output, "")
            self.assert_called_with('SoftLayer_Hardware_Server',
                                    'setUserMetadata',
                                    args=(['some data'],),
                                    identifier=1000)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_update_firmware(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['server', 'update-firmware', '1000'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")
        self.assert_called_with('SoftLayer_Hardware_Server',
                                'createFirmwareUpdateTransaction',
                                args=((1, 1, 1, 1)), identifier=1000)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_reflash_firmware(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['server', 'reflash-firmware', '1000'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")
        self.assert_called_with('SoftLayer_Hardware_Server',
                                'createFirmwareReflashTransaction',
                                args=((1, 1, 1)), identifier=1000)

    def test_edit(self):
        result = self.run_command(['server', 'edit',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--userdata="testdata"',
                                   '--tag=dev',
                                   '--tag=green',
                                   '--public-speed=10',
                                   '--redundant',
                                   '--private-speed=100',
                                   '--degraded',
                                   '100'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, '')

        self.assert_called_with(
            'SoftLayer_Hardware_Server', 'editObject',
            args=({'domain': 'example.com', 'hostname': 'host'},),
            identifier=100,
        )
        self.assert_called_with(
            'SoftLayer_Hardware_Server', 'setUserMetadata',
            args=(['"testdata"'],),
            identifier=100,
        )
        self.assert_called_with(
            'SoftLayer_Hardware_Server', 'setPublicNetworkInterfaceSpeed',
            args=([10, 'redundant'],),
            identifier=100,
        )
        self.assert_called_with(
            'SoftLayer_Hardware_Server', 'setPrivateNetworkInterfaceSpeed',
            args=([100, 'degraded'],),
            identifier=100,
        )

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_rescue(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['server', 'rescue', '1000'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")
        self.assert_called_with('SoftLayer_Hardware_Server', 'bootToRescueLayer', identifier=1000)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_server_rescue_negative(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['server', 'rescue', '1000'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_ready(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {
            "provisionDate": "2017-10-17T11:21:53-07:00",
            "id": 41957081
        }
        result = self.run_command(['hw', 'ready', '100'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, '"READY"\n')

    def test_not_ready(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        not_ready = {
            'activeTransaction': {
                'transactionStatus': {'friendlyName': 'Attach Primary Disk'}
            },
            'provisionDate': '',
            'id': 47392219
        }
        ready = {
            "provisionDate": "2017-10-17T11:21:53-07:00",
            "id": 41957081
        }
        mock.side_effect = [not_ready, ready]
        result = self.run_command(['hw', 'ready', '100'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('time.sleep')
    def test_going_ready(self, _sleep):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        not_ready = {
            'activeTransaction': {
                'transactionStatus': {'friendlyName': 'Attach Primary Disk'}
            },
            'provisionDate': '',
            'id': 47392219
        }
        ready = {
            "provisionDate": "2017-10-17T11:21:53-07:00",
            "id": 41957081
        }
        mock.side_effect = [not_ready, ready]
        result = self.run_command(['hw', 'ready', '100', '--wait=100'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, '"READY"\n')

    def test_toggle_ipmi_on(self):
        mock.return_value = True
        result = self.run_command(['server', 'toggle-ipmi', '--enable', '12345'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, 'True\n')

    def test_toggle_ipmi_off(self):
        mock.return_value = True
        result = self.run_command(['server', 'toggle-ipmi', '--disable', '12345'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, 'True\n')

    def test_bandwidth_hw(self):
        if sys.version_info < (3, 6):
            self.skipTest("Test requires python 3.6+")
        result = self.run_command(['server', 'bandwidth', '100', '--start_date=2019-01-01', '--end_date=2019-02-01'])
        self.assert_no_fail(result)

        date = '2019-05-20 23:00'
        # number of characters from the end of output to break so json can parse properly
        pivot = 157
        # only pyhon 3.7 supports the timezone format slapi uses
        if sys.version_info < (3, 7):
            date = '2019-05-20T23:00:00-06:00'
            pivot = 166
        # Since this is 2 tables, it gets returned as invalid json like "[{}][{}]"" instead of "[[{}],[{}]]"
        # so we just do some hacky string substitution to pull out the respective arrays that can be jsonifyied

        output_summary = json.loads(result.output[0:-pivot])
        output_list = json.loads(result.output[-pivot:])

        self.assertEqual(output_summary[0]['Average MBps'], 0.3841)
        self.assertEqual(output_summary[1]['Max Date'], date)
        self.assertEqual(output_summary[2]['Max GB'], 0.1172)
        self.assertEqual(output_summary[3]['Sum GB'], 0.0009)

        self.assertEqual(output_list[0]['Date'], date)
        self.assertEqual(output_list[0]['Pub In'], 1.3503)

    def test_bandwidth_hw_quite(self):
        result = self.run_command(['server', 'bandwidth', '100', '--start_date=2019-01-01',
                                   '--end_date=2019-02-01', '-q'])
        self.assert_no_fail(result)
        date = '2019-05-20 23:00'

        # only pyhon 3.7 supports the timezone format slapi uses
        if sys.version_info < (3, 7):
            date = '2019-05-20T23:00:00-06:00'

        output_summary = json.loads(result.output)

        self.assertEqual(output_summary[0]['Average MBps'], 0.3841)
        self.assertEqual(output_summary[1]['Max Date'], date)
        self.assertEqual(output_summary[2]['Max GB'], 0.1172)
        self.assertEqual(output_summary[3]['Sum GB'], 0.0009)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_dns_sync_both(self, confirm_mock):
        confirm_mock.return_value = True
        getReverseDomainRecords = self.set_mock('SoftLayer_Hardware_Server',
                                                'getReverseDomainRecords')
        getReverseDomainRecords.return_value = [{
            'networkAddress': '172.16.1.100',
            'name': '2.240.16.172.in-addr.arpa',
            'resourceRecords': [{'data': 'test.softlayer.com.',
                                 'id': 100,
                                 'host': '12'}],
            'updateDate': '2013-09-11T14:36:57-07:00',
            'serial': 1234665663,
            'id': 123456,
        }]
        getResourceRecords = self.set_mock('SoftLayer_Dns_Domain',
                                           'getResourceRecords')
        getResourceRecords.return_value = []
        createAargs = ({
                           'type': 'a',
                           'host': 'hardware-test1',
                           'domainId': 12345,  # from SoftLayer_Account::getDomains
                           'data': '172.16.1.100',
                           'ttl': 7200
                       },)
        createPTRargs = ({
                             'type': 'ptr',
                             'host': '100',
                             'domainId': 123456,
                             'data': 'hardware-test1.test.sftlyr.ws',
                             'ttl': 7200
                         },)

        result = self.run_command(['hw', 'dns-sync', '1000'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Dns_Domain', 'getResourceRecords')
        self.assert_called_with('SoftLayer_Hardware_Server',
                                'getReverseDomainRecords')
        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'createObject',
                                args=createAargs)
        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'createObject',
                                args=createPTRargs)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_dns_sync_v6(self, confirm_mock):
        confirm_mock.return_value = True
        getResourceRecords = self.set_mock('SoftLayer_Dns_Domain',
                                           'getResourceRecords')
        getResourceRecords.return_value = []
        server = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        test_server = {
            'id': 1000,
            'hostname': 'hardware-test1',
            'domain': 'sftlyr.ws',
            'primaryIpAddress': '172.16.1.100',
            'fullyQualifiedDomainName': 'hw-test1.sftlyr.ws',
            "primaryNetworkComponent": {}
        }
        server.return_value = test_server

        result = self.run_command(['hw', 'dns-sync', '--aaaa-record', '1000'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

        test_server['primaryNetworkComponent'] = {
            'primaryVersion6IpAddressRecord': {
                'ipAddress': '2607:f0d0:1b01:0023:0000:0000:0000:0004'
            }
        }
        createV6args = ({
                            'type': 'aaaa',
                            'host': 'hardware-test1',
                            'domainId': 12345,  # from SoftLayer_Account::getDomains
                            'data': '2607:f0d0:1b01:0023:0000:0000:0000:0004',
                            'ttl': 7200
                        },)
        server.return_value = test_server
        result = self.run_command(['hw', 'dns-sync', '--aaaa-record', '1000'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'createObject',
                                args=createV6args)

        v6Record = {
            'id': 1,
            'ttl': 7200,
            'data': '2607:f0d0:1b01:0023:0000:0000:0000:0004',
            'host': 'hardware-test1',
            'type': 'aaaa'
        }

        getResourceRecords = self.set_mock('SoftLayer_Dns_Domain',
                                           'getResourceRecords')
        getResourceRecords.return_value = [v6Record]
        editArgs = (v6Record,)
        result = self.run_command(['hw', 'dns-sync', '--aaaa-record', '1000'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'editObject',
                                args=editArgs)

        getResourceRecords = self.set_mock('SoftLayer_Dns_Domain',
                                           'getResourceRecords')
        getResourceRecords.return_value = [v6Record, v6Record]
        result = self.run_command(['hw', 'dns-sync', '--aaaa-record', '1000'])
        self.assertEqual(result.exit_code, 1)
        self.assertIsInstance(result.exception, SoftLayerError)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_dns_sync_edit_a(self, confirm_mock):
        confirm_mock.return_value = True
        getResourceRecords = self.set_mock('SoftLayer_Dns_Domain',
                                           'getResourceRecords')
        getResourceRecords.return_value = [
            {'id': 1, 'ttl': 7200, 'data': '1.1.1.1',
             'host': 'hardware-test1', 'type': 'a'}
        ]
        editArgs = (
            {'type': 'a', 'host': 'hardware-test1', 'data': '172.16.1.100',
             'id': 1, 'ttl': 7200},
        )
        result = self.run_command(['hw', 'dns-sync', '-a', '1000'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'editObject',
                                args=editArgs)

        getResourceRecords = self.set_mock('SoftLayer_Dns_Domain',
                                           'getResourceRecords')
        getResourceRecords.return_value = [
            {'id': 1, 'ttl': 7200, 'data': '1.1.1.1',
             'host': 'hardware-test1', 'type': 'a'},
            {'id': 2, 'ttl': 7200, 'data': '1.1.1.1',
             'host': 'hardware-test1', 'type': 'a'}
        ]
        result = self.run_command(['hw', 'dns-sync', '-a', '1000'])
        self.assertEqual(result.exit_code, 1)
        self.assertIsInstance(result.exception, SoftLayerError)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_dns_sync_edit_ptr(self, confirm_mock):
        confirm_mock.return_value = True
        getReverseDomainRecords = self.set_mock('SoftLayer_Hardware_Server',
                                                'getReverseDomainRecords')
        getReverseDomainRecords.return_value = [{
            'networkAddress': '172.16.1.100',
            'name': '100.1.16.172.in-addr.arpa',
            'resourceRecords': [{'data': 'test.softlayer.com.',
                                 'id': 123,
                                 'host': '100'}],
            'updateDate': '2013-09-11T14:36:57-07:00',
            'serial': 1234665663,
            'id': 123456,
        }]
        editArgs = ({'host': '100', 'data': 'hardware-test1.test.sftlyr.ws',
                     'id': 123, 'ttl': 7200},)
        result = self.run_command(['hw', 'dns-sync', '--ptr', '1000'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'editObject',
                                args=editArgs)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_dns_sync_misc_exception(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['hw', 'dns-sync', '-a', '1000'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

        guest = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        test_guest = {
            'id': 1000,
            'primaryIpAddress': '',
            'hostname': 'hardware-test1',
            'domain': 'sftlyr.ws',
            'fullyQualifiedDomainName': 'hardware-test1.sftlyr.ws',
            "primaryNetworkComponent": {}
        }
        guest.return_value = test_guest
        result = self.run_command(['hw', 'dns-sync', '-a', '1000'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_hardware_storage(self):
        result = self.run_command(
            ['hw', 'storage', '100'])

        self.assert_no_fail(result)

    def test_billing(self):
        result = self.run_command(['hw', 'billing', '123456'])
        billing_json = {
            'Billing Item Id': 6327,
            'Id': '123456',
            'Provision Date': None,
            'Recurring Fee': 1.54,
            'Total': 16.08,
            'prices': [{
                'Item': 'test',
                'Recurring Price': 1
            }]
        }
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), billing_json)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_hw_no_confirm(self, confirm_mock):
        confirm_mock.return_value = False

        result = self.run_command(['hw', 'create', '--hostname=test', '--size=S1270_8GB_2X1TBSATA_NORAID',
                                   '--domain=example.com', '--datacenter=TEST00',
                                   '--network=TEST_NETWORK', '--os=UBUNTU_12_64'])

        self.assertEqual(result.exit_code, 2)

    def test_get_hardware_guests(self):
        result = self.run_command(['hw', 'guests', '123456'])
        self.assert_no_fail(result)

    def test_hardware_guests_empty(self):
        mock = self.set_mock('SoftLayer_Virtual_Host', 'getGuests')
        mock.return_value = None

        result = self.run_command(['hw', 'guests', '123456'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_authorize_hw_no_confirm(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['hw', 'authorize-storage', '-u', '1234'])

        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_authorize_hw_empty(self, confirm_mock):
        confirm_mock.return_value = True
        storage_result = self.set_mock('SoftLayer_Account', 'getNetworkStorage')
        storage_result.return_value = []
        result = self.run_command(['hw', 'authorize-storage', '--username-storage=#', '1234'])

        self.assertEqual(str(result.exception), "The Storage with username: # was not found, "
                                                "please enter a valid storage username")

    def test_authorize_hw(self):
        result = self.run_command(['hw', 'authorize-storage', '--username-storage=SL01SEL301234-11', '1234'])
        self.assert_no_fail(result)

    def test_upgrade_no_options(self, ):
        result = self.run_command(['hw', 'upgrade', '100'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.ArgumentError)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_upgrade_aborted(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['hw', 'upgrade', '100', '--memory=1'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_upgrade_test(self):
        order_mock = self.set_mock('SoftLayer_Product_Order', 'verifyOrder')
        order_mock.return_value = SoftLayer_Product_Order.hardware_verifyOrder
        result = self.run_command(['hw', 'upgrade', '100', '--test', '--memory=32', '--public-bandwidth=500',
                                   '--drive-controller=RAID', '--network=10000 Redundant'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_upgrade_add_disk(self, confirm_mock):
        confirm_mock.return_value = True
        order_mock = self.set_mock('SoftLayer_Product_Order', 'placeOrder')
        order_mock.return_value = SoftLayer_Product_Order.hardware_placeOrder
        result = self.run_command(['hw', 'upgrade', '100', '--add-disk=1000', '2'])

        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_upgrade_resize_disk(self, confirm_mock):
        confirm_mock.return_value = True
        order_mock = self.set_mock('SoftLayer_Product_Order', 'placeOrder')
        order_mock.return_value = SoftLayer_Product_Order.hardware_placeOrder
        result = self.run_command(['hw', 'upgrade', '100', '--resize-disk=1000', '1'])

        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_upgrade_disk_not_price_found(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['hw', 'upgrade', '100', '--add-disk=1000', '3'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_upgrade_disk_already_exist(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['hw', 'upgrade', '100', '--add-disk=1000', '1'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_upgrade_disk_does_not_exist(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['hw', 'upgrade', '100', '--resize-disk=1000', '3'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_upgrade(self, confirm_mock):
        confirm_mock.return_value = True
        order_mock = self.set_mock('SoftLayer_Product_Order', 'placeOrder')
        order_mock.return_value = SoftLayer_Product_Order.hardware_placeOrder
        result = self.run_command(['hw', 'upgrade', '100', '--memory=32', '--public-bandwidth=500',
                                   '--drive-controller=RAID', '--network=10000 Redundant'])

        self.assert_no_fail(result)

    def test_components(self):
        result = self.run_command(['hardware', 'detail', '100', '--components'])
        self.assert_no_fail(result)
