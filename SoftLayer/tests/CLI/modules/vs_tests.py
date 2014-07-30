"""
    SoftLayer.tests.CLI.modules.vs_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from mock import patch

from SoftLayer.tests import TestCase, FixtureClient
from SoftLayer.CLI.helpers import format_output
from SoftLayer.CLI.modules import vs


class DnsTests(TestCase):

    def set_up(self):
        self.client = FixtureClient()

    def test_list_vs(self):
        command = vs.ListVSIs(client=self.client)

        output = command.execute({'--tags': 'tag'})
        self.assertEqual([{'datacenter': 'TEST00',
                           'primary_ip': '172.16.240.2',
                           'host': 'vs-test1.test.sftlyr.ws',
                           'memory': 1024,
                           'cores': 2,
                           'active_transaction': None,
                           'id': 100,
                           'backend_ip': '10.45.19.37',
                           'owner': 'chechu'},
                          {'datacenter': 'TEST00',
                           'primary_ip': '172.16.240.7',
                           'host': 'vs-test2.test.sftlyr.ws',
                           'memory': 4096,
                           'cores': 4,
                           'active_transaction': None,
                           'id': 104,
                           'backend_ip': '10.45.19.35',
                           'owner': 'chechu'}],
                         format_output(output, 'python'))

    def test_detail_vs(self):
        command = vs.VSDetails(client=self.client)
        output = command.execute({'<identifier>': '100',
                                  '--passwords': True,
                                  '--price': True})

        self.assertEqual({'active_transaction': None,
                          'cores': 2,
                          'created': '2013-08-01 15:23:45',
                          'datacenter': 'TEST00',
                          'hostname': 'vs-test1.test.sftlyr.ws',
                          'id': 100,
                          'memory': 1024,
                          'modified': {},
                          'os': '12.04-64 Minimal for CCI',
                          'os_version': '12.04-64 Minimal for CCI',
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
                          'owner': 'chechu'},
                         format_output(output, 'python'))

    def test_create_options(self):
        command = vs.CreateOptionsVS(client=self.client)

        output = command.execute({'--all': True,
                                  '--cpu': True,
                                  '--datacenter': True,
                                  '--disk': True,
                                  '--memory': True,
                                  '--nic': True,
                                  '--os': True})

        self.assertEqual({'cpus (private)': [],
                          'cpus (standard)': ['1', '2', '3', '4'],
                          'datacenter': ['ams01', 'dal05'],
                          'local disk(0)': ['25', '100'],
                          'memory': ['1024', '2048', '3072', '4096'],
                          'nic': ['10', '100', '1000'],
                          'os (CENTOS)': 'CENTOS_6_64',
                          'os (DEBIAN)': 'DEBIAN_7_64',
                          'os (UBUNTU)': 'UBUNTU_12_64'},
                         format_output(output, 'python'))

    @patch('SoftLayer.CLI.modules.vs.confirm')
    def test_create(self, confirm_mock):
        confirm_mock.return_value = True
        command = vs.CreateVS(client=self.client)

        output = command.execute({'--cpu': '2',
                                  '--domain': 'example.com',
                                  '--hostname': 'host',
                                  '--image': None,
                                  '--os': 'UBUNTU_LATEST',
                                  '--memory': '1024',
                                  '--nic': '100',
                                  '--hourly': True,
                                  '--monthly': False,
                                  '--like': None,
                                  '--datacenter': None,
                                  '--dedicated': False,
                                  '--san': False,
                                  '--test': False,
                                  '--export': None,
                                  '--userfile': None,
                                  '--postinstall': None,
                                  '--key': [],
                                  '--like': [],
                                  '--network': [],
                                  '--disk': [],
                                  '--private': False,
                                  '--template': None,
                                  '--userdata': None,
                                  '--vlan_public': None,
                                  '--vlan_private': None,
                                  '--wait': None,
                                  '--really': False})

        self.assertEqual([{'guid': '1a2b3c-1701',
                           'id': 100,
                           'created': '2013-08-01 15:23:45'}],
                         format_output(output, 'python'))
