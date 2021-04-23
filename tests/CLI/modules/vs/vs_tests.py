"""
    SoftLayer.tests.CLI.modules.vs_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
import sys

from unittest import mock as mock

from SoftLayer.CLI import exceptions
from SoftLayer.fixtures import SoftLayer_Virtual_Guest as SoftLayer_Virtual_Guest
from SoftLayer import SoftLayerAPIError
from SoftLayer import SoftLayerError
from SoftLayer import testing


class VirtTests(testing.TestCase):

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_rescue_vs(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'rescue', '100'])

        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_rescue_vs_no_confirm(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['vs', 'rescue', '100'])

        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_reboot_vs_default(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'rebootDefault')
        mock.return_value = 'true'
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'reboot', '100'])

        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_reboot_vs_no_confirm(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'rebootDefault')
        mock.return_value = 'true'
        confirm_mock.return_value = False
        result = self.run_command(['vs', 'reboot', '100'])

        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_reboot_vs_soft(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'rebootSoft')
        mock.return_value = 'true'
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'reboot', '--soft', '100'])

        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_reboot_vs_hard(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'rebootHard')
        mock.return_value = 'true'
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'reboot', '--hard', '100'])

        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_power_vs_off_soft(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'powerOffSoft')
        mock.return_value = 'true'
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'power-off', '100'])

        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_power_off_vs_no_confirm(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'powerOffSoft')
        mock.return_value = 'true'
        confirm_mock.return_value = False

        result = self.run_command(['vs', 'power-off', '100'])

        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_power_off_vs_hard(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'powerOff')
        mock.return_value = 'true'
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'power-off', '--hard', '100'])

        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_power_on_vs(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'powerOn')
        mock.return_value = 'true'
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'power-on', '100'])

        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_pause_vs(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'pause')
        mock.return_value = 'true'
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'pause', '100'])

        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_pause_vs_no_confirm(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'pause')
        mock.return_value = 'true'
        confirm_mock.return_value = False

        result = self.run_command(['vs', 'pause', '100'])

        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_resume_vs(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'resume')
        mock.return_value = 'true'
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'resume', '100'])

        self.assert_no_fail(result)

    def test_list_vs(self):
        result = self.run_command(['vs', 'list', '--tag=tag'])

        self.assert_no_fail(result)

    @mock.patch('SoftLayer.utils.lookup')
    def test_detail_vs_empty_billing(self, mock_lookup):
        def mock_lookup_func(dic, key, *keys):
            if key == 'billingItem':
                return []
            if keys:
                return mock_lookup_func(dic.get(key, {}), keys[0], *keys[1:])
            return dic.get(key)

        mock_lookup.side_effect = mock_lookup_func

        result = self.run_command(['vs', 'detail', '100', '--passwords', '--price'])

        self.assert_no_fail(result)
        output = json.loads(result.output)
        self.assertEqual(output['owner'], None)

    def test_detail_vs(self):
        result = self.run_command(['vs', 'detail', '100', '--passwords', '--price'])

        self.assert_no_fail(result)
        output = json.loads(result.output)
        self.assertEqual(output['notes'], 'notes')
        self.assertEqual(output['price_rate'], 6.54)
        self.assertEqual(output['users'][0]['username'], 'user')
        self.assertEqual(output['vlans'][0]['number'], 23)
        self.assertEqual(output['owner'], 'chechu')
        self.assertEqual(output['Bandwidth'][0]['Allotment'], '250')

    def test_detail_vs_empty_tag(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getObject')
        mock.return_value = {
            'id': 100,
            'maxCpu': 2,
            'maxMemory': 1024,
            'tagReferences': [
                {'tag': {'name': 'example-tag'}},
                {},
            ],
        }
        result = self.run_command(['vs', 'detail', '100'])

        self.assert_no_fail(result)
        self.assertEqual(
            json.loads(result.output)['tags'],
            ['example-tag'],
        )

    def test_detail_vs_empty_allotment(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getBandwidthAllotmentDetail')
        mock.return_value = None
        result = self.run_command(['vs', 'detail', '100'])

        self.assert_no_fail(result)
        self.assertEqual(
            json.loads(result.output)['Bandwidth'][0]['Allotment'],
            '-',
        )

    def test_detail_drives_system(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getBlockDevices')
        mock.return_value = [
            {
                "createDate": "2018-10-06T04:27:35-06:00",
                "device": "0",
                "id": 11111,
                "mountType": "Disk",
                "diskImage": {
                    "capacity": 100,
                    "description": "adns.vmware.com",
                    "id": 72222,
                    "name": "adns.vmware.com",
                    "units": "GB",
                }
            }
        ]
        result = self.run_command(['vs', 'detail', '100'])

        self.assert_no_fail(result)
        output = json.loads(result.output)
        self.assertEqual(output['drives'][0]['Capacity'], '100 GB')
        self.assertEqual(output['drives'][0]['Name'], 'Disk')
        self.assertEqual(output['drives'][0]['Type'], 'System')

    def test_detail_drives_swap(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getBlockDevices')
        mock.return_value = [
            {
                "device": "1",
                "id": 22222,
                "mountType": "Disk",
                "statusId": 1,
                "diskImage": {
                    "capacity": 2,
                    "description": "6211111-SWAP",
                    "id": 33333,
                    "name": "6211111-SWAP",
                    "units": "GB",
                }
            }
        ]
        result = self.run_command(['vs', 'detail', '100'])

        self.assert_no_fail(result)
        output = json.loads(result.output)
        self.assertEqual(output['drives'][0]['Capacity'], '2 GB')
        self.assertEqual(output['drives'][0]['Name'], 'Disk')
        self.assertEqual(output['drives'][0]['Type'], 'Swap')

    def test_detail_vs_dedicated_host_not_found(self):
        ex = SoftLayerAPIError('SoftLayer_Exception', 'Not found')
        mock = self.set_mock('SoftLayer_Virtual_DedicatedHost', 'getObject')
        mock.side_effect = ex
        result = self.run_command(['vs', 'detail', '100'])
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output)['dedicated_host_id'], 37401)
        self.assertIsNone(json.loads(result.output)['dedicated_host'])

    def test_detail_vs_no_dedicated_host_hostname(self):
        mock = self.set_mock('SoftLayer_Virtual_DedicatedHost', 'getObject')
        mock.return_value = {'this_is_a_fudged_Virtual_DedicatedHost': True,
                             'name_is_not_provided': ''}
        result = self.run_command(['vs', 'detail', '100'])
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output)['dedicated_host_id'], 37401)
        self.assertIsNone(json.loads(result.output)['dedicated_host'])

    def test_detail_vs_security_group(self):
        vg_return = SoftLayer_Virtual_Guest.getObject
        sec_group = [
            {
                'id': 35386715,
                'name': 'eth',
                'port': 0,
                'speed': 100,
                'status': 'ACTIVE',
                'primaryIpAddress': '10.175.106.149',
                'securityGroupBindings': [
                    {
                        'id': 1620971,
                        'networkComponentId': 35386715,
                        'securityGroupId': 128321,
                        'securityGroup': {
                            'id': 128321,
                            'name': 'allow_all'
                        }
                    }
                ]
            }
        ]

        vg_return['networkComponents'] = sec_group
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getObject')
        mock.return_value = vg_return
        result = self.run_command(['vs', 'detail', '100'])
        self.assert_no_fail(result)
        output = json.loads(result.output)
        self.assertEqual(output['security_groups'][0]['id'], 128321)
        self.assertEqual(output['security_groups'][0]['name'], 'allow_all')
        self.assertEqual(output['security_groups'][0]['interface'], 'PRIVATE')

    def test_detail_vs_ptr_error(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getReverseDomainRecords')
        mock.side_effect = SoftLayerAPIError("SoftLayer_Exception", "Not Found")
        result = self.run_command(['vs', 'detail', '100'])
        self.assert_no_fail(result)
        output = json.loads(result.output)
        self.assertEqual(output.get('ptr', None), None)

    def test_create_options(self):
        result = self.run_command(['vs', 'create-options', '--vsi-type', 'TRANSIENT_CLOUD_SERVER'])
        self.assert_no_fail(result)

    def test_create_options_prices(self):
        result = self.run_command(['vs', 'create-options', '--prices', '--vsi-type', 'TRANSIENT_CLOUD_SERVER'])
        self.assert_no_fail(result)

    def test_create_options_prices_location(self):
        result = self.run_command(['vs', 'create-options', '--prices', 'dal13',
                                  '--vsi-type', 'TRANSIENT_CLOUD_SERVER'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_dns_sync_both(self, confirm_mock):
        confirm_mock.return_value = True
        getReverseDomainRecords = self.set_mock('SoftLayer_Virtual_Guest',
                                                'getReverseDomainRecords')
        getReverseDomainRecords.return_value = [{
            'networkAddress': '172.16.240.2',
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
            'host': 'vs-test1',
            'domainId': 12345,  # from SoftLayer_Account::getDomains
            'data': '172.16.240.2',
            'ttl': 7200
        },)
        createPTRargs = ({
            'type': 'ptr',
            'host': '2',
            'domainId': 123456,
            'data': 'vs-test1.test.sftlyr.ws',
            'ttl': 7200
        },)

        result = self.run_command(['vs', 'dns-sync', '100'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Dns_Domain', 'getResourceRecords')
        self.assert_called_with('SoftLayer_Virtual_Guest',
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
        guest = self.set_mock('SoftLayer_Virtual_Guest', 'getObject')
        test_guest = {
            'id': 100,
            'hostname': 'vs-test1',
            'domain': 'sftlyr.ws',
            'primaryIpAddress': '172.16.240.2',
            'fullyQualifiedDomainName': 'vs-test1.sftlyr.ws',
            "primaryNetworkComponent": {}
        }
        guest.return_value = test_guest

        result = self.run_command(['vs', 'dns-sync', '--aaaa-record', '100'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

        test_guest['primaryNetworkComponent'] = {
            'primaryVersion6IpAddressRecord': {
                'ipAddress': '2607:f0d0:1b01:0023:0000:0000:0000:0004'
            }
        }
        createV6args = ({
            'type': 'aaaa',
            'host': 'vs-test1',
            'domainId': 12345,
            'data': '2607:f0d0:1b01:0023:0000:0000:0000:0004',
            'ttl': 7200
        },)
        guest.return_value = test_guest
        result = self.run_command(['vs', 'dns-sync', '--aaaa-record', '100'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'createObject',
                                args=createV6args)

        v6Record = {
            'id': 1,
            'ttl': 7200,
            'data': '2607:f0d0:1b01:0023:0000:0000:0000:0004',
            'host': 'vs-test1',
            'type': 'aaaa'
        }

        getResourceRecords = self.set_mock('SoftLayer_Dns_Domain',
                                           'getResourceRecords')
        getResourceRecords.return_value = [v6Record]
        editArgs = (v6Record,)
        result = self.run_command(['vs', 'dns-sync', '--aaaa-record', '100'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'editObject',
                                args=editArgs)

        getResourceRecords = self.set_mock('SoftLayer_Dns_Domain',
                                           'getResourceRecords')
        getResourceRecords.return_value = [v6Record, v6Record]
        result = self.run_command(['vs', 'dns-sync', '--aaaa-record', '100'])
        self.assertEqual(result.exit_code, 1)
        self.assertIsInstance(result.exception, SoftLayerError)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_dns_sync_edit_a(self, confirm_mock):
        confirm_mock.return_value = True
        getResourceRecords = self.set_mock('SoftLayer_Dns_Domain',
                                           'getResourceRecords')
        getResourceRecords.return_value = [
            {'id': 1, 'ttl': 7200, 'data': '1.1.1.1',
             'host': 'vs-test1', 'type': 'a'}
        ]
        editArgs = (
            {'type': 'a', 'host': 'vs-test1', 'data': '172.16.240.2',
             'id': 1, 'ttl': 7200},
        )
        result = self.run_command(['vs', 'dns-sync', '-a', '100'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'editObject',
                                args=editArgs)

        getResourceRecords = self.set_mock('SoftLayer_Dns_Domain',
                                           'getResourceRecords')
        getResourceRecords.return_value = [
            {'id': 1, 'ttl': 7200, 'data': '1.1.1.1',
             'host': 'vs-test1', 'type': 'a'},
            {'id': 2, 'ttl': 7200, 'data': '1.1.1.1',
             'host': 'vs-test1', 'type': 'a'}
        ]
        result = self.run_command(['vs', 'dns-sync', '-a', '100'])
        self.assertEqual(result.exit_code, 1)
        self.assertIsInstance(result.exception, SoftLayerError)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_dns_sync_edit_ptr(self, confirm_mock):
        confirm_mock.return_value = True
        getReverseDomainRecords = self.set_mock('SoftLayer_Virtual_Guest',
                                                'getReverseDomainRecords')
        getReverseDomainRecords.return_value = [{
            'networkAddress': '172.16.240.2',
            'name': '2.240.16.172.in-addr.arpa',
            'resourceRecords': [{'data': 'test.softlayer.com.',
                                 'id': 100,
                                 'host': '2'}],
            'updateDate': '2013-09-11T14:36:57-07:00',
            'serial': 1234665663,
            'id': 123456,
        }]
        editArgs = ({'host': '2', 'data': 'vs-test1.test.sftlyr.ws',
                     'id': 100, 'ttl': 7200},)
        result = self.run_command(['vs', 'dns-sync', '--ptr', '100'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'editObject',
                                args=editArgs)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_dns_sync_misc_exception(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['vs', 'dns-sync', '-a', '100'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

        guest = self.set_mock('SoftLayer_Virtual_Guest', 'getObject')
        test_guest = {
            'id': 100,
            'primaryIpAddress': '',
            'hostname': 'vs-test1',
            'domain': 'sftlyr.ws',
            'fullyQualifiedDomainName': 'vs-test1.sftlyr.ws',
            "primaryNetworkComponent": {}
        }
        guest.return_value = test_guest
        result = self.run_command(['vs', 'dns-sync', '-a', '100'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_upgrade_no_options(self, ):
        result = self.run_command(['vs', 'upgrade', '100'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.ArgumentError)

    def test_upgrade_private_no_cpu(self):
        result = self.run_command(['vs', 'upgrade', '100', '--private',
                                   '--memory=1024'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.ArgumentError)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_upgrade_aborted(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['vs', 'upgrade', '100', '--cpu=1'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_upgrade(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'upgrade', '100', '--cpu=4',
                                   '--memory=2048', '--network=1000'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertIn({'id': 1144}, order_container['prices'])
        self.assertIn({'id': 1133}, order_container['prices'])
        self.assertIn({'id': 1122}, order_container['prices'])
        self.assertEqual(order_container['virtualGuests'], [{'id': 100}])

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_upgrade_disk(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'upgrade', '100', '--flavor=M1_64X512X100',
                                   '--resize-disk=10', '1', '--resize-disk=10', '2'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertEqual(799, order_container['presetId'])
        self.assertIn({'id': 100}, order_container['virtualGuests'])
        self.assertEqual(order_container['virtualGuests'], [{'id': 100}])

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_upgrade_disk_error(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'upgrade', '100', '--flavor=M1_64X512X100',
                                   '--resize-disk=1000', '1', '--resize-disk=10', '2'])
        self.assertEqual(result.exit_code, 1)
        self.assertIsInstance(result.exception, SoftLayerAPIError)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_upgrade_with_flavor(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'upgrade', '100', '--flavor=M1_64X512X100'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertEqual(799, order_container['presetId'])
        self.assertIn({'id': 100}, order_container['virtualGuests'])
        self.assertEqual(order_container['virtualGuests'], [{'id': 100}])

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_upgrade_with_add_disk(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'upgrade', '100', '--add-disk=10', '--add-disk=10'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertIn({'id': 100}, order_container['virtualGuests'])
        self.assertEqual(order_container['virtualGuests'], [{'id': 100}])

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_upgrade_with_cpu_memory_and_flavor(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'upgrade', '100', '--cpu=4',
                                   '--memory=1024', '--flavor=M1_64X512X100'])
        self.assertEqual(result.exit_code, 1)
        self.assertIsInstance(result.exception, ValueError)

    def test_edit(self):
        result = self.run_command(['vs', 'edit',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--userdata="testdata"',
                                   '--tag=dev',
                                   '--tag=green',
                                   '--public-speed=10',
                                   '--private-speed=100',
                                   '100'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, '')

        self.assert_called_with(
            'SoftLayer_Virtual_Guest', 'editObject',
            args=({'domain': 'example.com', 'hostname': 'host'},),
            identifier=100,
        )
        self.assert_called_with(
            'SoftLayer_Virtual_Guest', 'setUserMetadata',
            args=(['"testdata"'],),
            identifier=100,
        )
        self.assert_called_with(
            'SoftLayer_Virtual_Guest', 'setPublicNetworkInterfaceSpeed',
            args=(10,),
            identifier=100,
        )
        self.assert_called_with(
            'SoftLayer_Virtual_Guest', 'setPrivateNetworkInterfaceSpeed',
            args=(100,),
            identifier=100,
        )

    def test_ready(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getObject')
        mock.return_value = {
            "provisionDate": "2017-10-17T11:21:53-07:00",
            "id": 41957081
        }
        result = self.run_command(['vs', 'ready', '100'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, '"READY"\n')

    def test_not_ready(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getObject')
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
        result = self.run_command(['vs', 'ready', '100'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('time.sleep')
    def test_going_ready(self, _sleep):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getObject')
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
        result = self.run_command(['vs', 'ready', '100', '--wait=100'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, '"READY"\n')

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_reload(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'reloadCurrentOperatingSystemConfguration')
        confirm_mock.return_value = True
        mock.return_value = 'true'

        result = self.run_command(['vs', 'reload', '--postinstall', '100', '--key', '100', '--image', '100', '100'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_reload_no_confirm(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'reloadCurrentOperatingSystemConfiguration')
        confirm_mock.return_value = False
        mock.return_value = 'false'

        result = self.run_command(['vs', 'reload', '--postinstall', '100', '--key', '100', '--image', '100', '100'])
        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_cancel(self, confirm_mock):
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'cancel', '100'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_cancel_no_confirm(self, confirm_mock):
        confirm_mock.return_value = False

        result = self.run_command(['vs', 'cancel', '100'])
        self.assertEqual(result.exit_code, 2)

    def test_vs_capture(self):

        result = self.run_command(['vs', 'capture', '100', '--name', 'TestName'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'createArchiveTransaction', identifier=100)

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_usage_no_confirm(self, confirm_mock):
        confirm_mock.return_value = False

        result = self.run_command(['vs', 'usage', '100'])
        self.assertEqual(result.exit_code, 2)

    def test_usage_vs(self):
        result = self.run_command(
            ['vs', 'usage', '100'])
        self.assertEqual(result.exit_code, 2)

    def test_usage_vs_cpu(self):
        result = self.run_command(
            ['vs', 'usage', '100', '--start_date=2019-3-4', '--end_date=2019-4-2', '--valid_type=CPU0',
             '--summary_period=300'])

        self.assert_no_fail(result)

    def test_usage_vs_memory(self):
        result = self.run_command(
            ['vs', 'usage', '100', '--start_date=2019-3-4', '--end_date=2019-4-2', '--valid_type=MEMORY_USAGE',
             '--summary_period=300'])

        self.assert_no_fail(result)

    def test_usage_metric_data_empty(self):
        usage_vs = self.set_mock('SoftLayer_Metric_Tracking_Object', 'getSummaryData')
        test_usage = []
        usage_vs.return_value = test_usage
        result = self.run_command(
            ['vs', 'usage', '100', '--start_date=2019-3-4', '--end_date=2019-4-2', '--valid_type=CPU0',
             '--summary_period=300'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_bandwidth_vs(self):
        if sys.version_info < (3, 6):
            self.skipTest("Test requires python 3.6+")

        result = self.run_command(['vs', 'bandwidth', '100', '--start_date=2019-01-01', '--end_date=2019-02-01'])
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

    def test_bandwidth_vs_quite(self):
        result = self.run_command(['vs', 'bandwidth', '100', '--start_date=2019-01-01', '--end_date=2019-02-01', '-q'])
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

    def test_vs_storage(self):
        result = self.run_command(
            ['vs', 'storage', '100'])

        self.assert_no_fail(result)

    def test_billing(self):
        result = self.run_command(['vs', 'billing', '123456'])
        vir_billing = {
            'Billing Item Id': 6327,
            'Id': '123456',
            'Provision Date': None,
            'Recurring Fee': None,
            'Total': 1.54,
            'prices': [
                {'Recurring Price': 1},
                {'Recurring Price': 1},
                {'Recurring Price': 1},
                {'Recurring Price': 1},
                {'Recurring Price': 1}
            ]
        }
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), vir_billing)

    def test_vs_migrate_list(self):
        result = self.run_command(['vs', 'migrate'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getVirtualGuests')
        self.assert_not_called_with('SoftLayer_Virtual_Guest', 'migrate')
        self.assert_not_called_with('SoftLayer_Virtual_Guest', 'migrateDedicatedHost')

    def test_vs_migrate_list_empty(self):
        mock = self.set_mock('SoftLayer_Account', 'getVirtualGuests')
        mock.return_value = []
        result = self.run_command(['vs', 'migrate'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getVirtualGuests')
        self.assert_not_called_with('SoftLayer_Virtual_Guest', 'migrate')
        self.assert_not_called_with('SoftLayer_Virtual_Guest', 'migrateDedicatedHost')
        self.assertIn("No guests require migration at this time", result.output)

    def test_vs_migrate_guest(self):
        result = self.run_command(['vs', 'migrate', '-g', '100'])
        self.assert_no_fail(result)
        self.assertIn('Started a migration on', result.output)
        self.assert_not_called_with('SoftLayer_Account', 'getVirtualGuests')
        self.assert_called_with('SoftLayer_Virtual_Guest', 'migrate', identifier=100)
        self.assert_not_called_with('SoftLayer_Virtual_Guest', 'migrateDedicatedHost')

    def test_vs_migrate_all(self):
        result = self.run_command(['vs', 'migrate', '-a'])
        self.assert_no_fail(result)
        self.assertIn('Started a migration on', result.output)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'migrate', identifier=100)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'migrate', identifier=104)
        self.assert_not_called_with('SoftLayer_Virtual_Guest', 'migrateDedicatedHost')

    def test_vs_migrate_all_empty(self):
        mock = self.set_mock('SoftLayer_Account', 'getVirtualGuests')
        mock.return_value = []
        result = self.run_command(['vs', 'migrate', '-a'])
        self.assert_no_fail(result)
        self.assertIn('No guests require migration at this time', result.output)

    def test_vs_migrate_dedicated(self):
        result = self.run_command(['vs', 'migrate', '-g', '100', '-h', '999'])
        self.assert_no_fail(result)
        self.assertIn('Started a migration on', result.output)
        self.assert_not_called_with('SoftLayer_Account', 'getVirtualGuests')
        self.assert_not_called_with('SoftLayer_Virtual_Guest', 'migrate', identifier=100)
        self.assert_not_called_with('SoftLayer_Virtual_Guest', 'migrateDedicatedHost', args=(999), identifier=100)

    def test_vs_migrate_exception(self):
        ex = SoftLayerAPIError('SoftLayer_Exception', 'PROBLEM')
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'migrate')
        mock.side_effect = ex
        result = self.run_command(['vs', 'migrate', '-g', '100'])
        self.assert_no_fail(result)
        self.assertIn('Failed to migrate', result.output)
        self.assert_not_called_with('SoftLayer_Account', 'getVirtualGuests')
        self.assert_called_with('SoftLayer_Virtual_Guest', 'migrate', identifier=100)
        self.assert_not_called_with('SoftLayer_Virtual_Guest', 'migrateDedicatedHost', args=(999), identifier=100)

    def test_list_vsi(self):
        result = self.run_command(['vs', 'list', '--hardware'])
        self.assert_no_fail(result)

    def test_credentail(self):
        result = self.run_command(['vs', 'credentials', '100'])
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), [{
            "username": "user",
            "password": "pass"
        }])

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_authorize_storage_vs_no_confirm(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['vs', 'authorize-storage', '-u', '1234'])

        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_authorize_vs_empty(self, confirm_mock):
        confirm_mock.return_value = True
        storage_result = self.set_mock('SoftLayer_Account', 'getNetworkStorage')
        storage_result.return_value = []
        result = self.run_command(['vs', 'authorize-storage', '--username-storage=#', '1234'])

        self.assertEqual(str(result.exception), "The Storage with username: # was not found, "
                                                "please enter a valid storage username")

    def test_authorize_storage_vs(self):
        result = self.run_command(['vs', 'authorize-storage', '--username-storage=SL01SEL301234-11', '1234'])
        self.assert_no_fail(result)

    def test_authorize_portable_storage_vs(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'attachDiskImage')
        mock.return_value = {
            "createDate": "2021-03-22T13:15:31-06:00",
            "id": 1234567
        }
        result = self.run_command(['vs', 'authorize-storage', '--portable-id=12345', '1234'])
        self.assert_no_fail(result)

    def test_authorize_volume_and_portable_storage_vs(self):
        result = self.run_command(['vs', 'authorize-storage', '--username-storage=SL01SEL301234-11',
                                   '--portable-id=12345', '1234'])
        self.assert_no_fail(result)
