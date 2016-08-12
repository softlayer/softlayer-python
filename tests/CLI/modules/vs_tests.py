"""
    SoftLayer.tests.CLI.modules.vs_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json

import mock

from SoftLayer.CLI import exceptions
from SoftLayer import testing


class VirtTests(testing.TestCase):

    def test_list_vs(self):
        result = self.run_command(['vs', 'list', '--tag=tag'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{'datacenter': 'TEST00',
                           'primary_ip': '172.16.240.2',
                           'hostname': 'vs-test1',
                           'action': None,
                           'id': 100,
                           'backend_ip': '10.45.19.37'},
                          {'datacenter': 'TEST00',
                           'primary_ip': '172.16.240.7',
                           'hostname': 'vs-test2',
                           'action': None,
                           'id': 104,
                           'backend_ip': '10.45.19.35'}])

    def test_detail_vs(self):
        result = self.run_command(['vs', 'detail', '100',
                                   '--passwords', '--price'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         {'active_transaction': None,
                          'cores': 2,
                          'created': '2013-08-01 15:23:45',
                          'datacenter': 'TEST00',
                          'hostname': 'vs-test1',
                          'domain': 'test.sftlyr.ws',
                          'fqdn': 'vs-test1.test.sftlyr.ws',
                          'id': 100,
                          'guid': '1a2b3c-1701',
                          'memory': 1024,
                          'modified': {},
                          'os': '12.04-64 Minimal for VSI',
                          'os_version': '12.04-64 Minimal for VSI',
                          'notes': 'notes',
                          'price rate': 1.54,
                          'tags': ['production'],
                          'private_cpu': {},
                          'private_ip': '10.45.19.37',
                          'private_only': {},
                          'ptr': 'test.softlayer.com.',
                          'public_ip': '172.16.240.2',
                          'state': 'RUNNING',
                          'status': 'ACTIVE',
                          'users': [{'software': 'Ubuntu',
                                     'password': 'pass',
                                     'username': 'user'}],
                          'vlans': [{'type': 'PUBLIC',
                                     'number': 23,
                                     'id': 1}],
                          'owner': 'chechu'})

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

    def test_create_options(self):
        result = self.run_command(['vs', 'create-options'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         {'cpus (private)': [],
                          'cpus (standard)': ['1', '2', '3', '4'],
                          'datacenter': ['ams01', 'dal05'],
                          'local disk(0)': ['25', '100'],
                          'memory': ['1024', '2048', '3072', '4096'],
                          'nic': ['10', '100', '1000'],
                          'os (CENTOS)': 'CENTOS_6_64',
                          'os (DEBIAN)': 'DEBIAN_7_64',
                          'os (UBUNTU)': 'UBUNTU_12_64'})

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'create',
                                   '--cpu=2',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--os=UBUNTU_LATEST',
                                   '--memory=1',
                                   '--network=100',
                                   '--billing=hourly',
                                   '--datacenter=dal05',
                                   '--tag=dev',
                                   '--tag=green'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         {'guid': '1a2b3c-1701',
                          'id': 100,
                          'created': '2013-08-01 15:23:45'})

        args = ({'datacenter': {'name': 'dal05'},
                 'domain': 'example.com',
                 'hourlyBillingFlag': True,
                 'localDiskFlag': True,
                 'maxMemory': 1024,
                 'hostname': 'host',
                 'startCpus': 2,
                 'operatingSystemReferenceCode': 'UBUNTU_LATEST',
                 'networkComponents': [{'maxSpeed': '100'}]},)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'createObject',
                                args=args)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_with_integer_image_id(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'create',
                                   '--cpu=2',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--image=12345',
                                   '--memory=1',
                                   '--network=100',
                                   '--billing=hourly',
                                   '--datacenter=dal05'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         {'guid': '1a2b3c-1701',
                          'id': 100,
                          'created': '2013-08-01 15:23:45'})

        args = ({
            'datacenter': {'name': 'dal05'},
            'domain': 'example.com',
            'hourlyBillingFlag': True,
            'localDiskFlag': True,
            'maxMemory': 1024,
            'hostname': 'host',
            'startCpus': 2,
            'blockDeviceTemplateGroup': {
                'globalIdentifier': '0B5DEAF4-643D-46CA-A695-CECBE8832C9D',
            },
            'networkComponents': [{'maxSpeed': '100'}]
        },)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'createObject',
                                args=args)

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
            'domainId': 98765,
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
            'domainId': 98765,
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
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

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
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

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
