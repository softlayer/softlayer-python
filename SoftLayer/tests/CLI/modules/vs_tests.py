"""
    SoftLayer.tests.CLI.modules.vs_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

from SoftLayer import testing

import json


class DnsTests(testing.TestCase):

    def test_list_vs(self):
        result = self.run_command(['vs', 'list', '--tags=tag'])

        self.assertEqual(result.exit_code, 0)
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

        self.assertEqual(result.exit_code, 0)
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
                          'users': [{'password': 'pass', 'username': 'user'}],
                          'vlans': [{'type': 'PUBLIC',
                                     'number': 23,
                                     'id': 1}],
                          'owner': 'chechu'})

    def test_create_options(self):
        result = self.run_command(['vs', 'create-options'])

        self.assertEqual(result.exit_code, 0)
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
                                   '--tag=dev',
                                   '--tag=green'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output),
                         {'guid': '1a2b3c-1701',
                          'id': 100,
                          'created': '2013-08-01 15:23:45'})

        args = ({'domain': 'example.com',
                 'hourlyBillingFlag': True,
                 'localDiskFlag': True,
                 'maxMemory': 1024,
                 'hostname': 'host',
                 'startCpus': 2,
                 'operatingSystemReferenceCode': 'UBUNTU_LATEST',
                 'networkComponents': [{'maxSpeed': '100'}]},)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'createObject',
                                args=args)
