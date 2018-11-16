"""
    SoftLayer.tests.CLI.modules.subnet_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing

import json


class SubnetTests(testing.TestCase):
    def test_detail(self):
        result = self.run_command(['subnet', 'detail', '1234'])

        self.assert_no_fail(result)
        self.assertEqual(
            {
                'id': 1234,
                'identifier': '1.2.3.4/26',
                'subnet type': 'ADDITIONAL_PRIMARY',
                'network space': 'PUBLIC',
                'gateway': '1.2.3.254',
                'broadcast': '1.2.3.255',
                'datacenter': 'dal10',
                'vs': [
                    {
                        'hostname': 'hostname0',
                        'domain': 'sl.test',
                        'public_ip': '1.2.3.10',
                        'private_ip': '10.0.1.2'
                    }
                ],
                'hardware': 'none',
                'usable ips': 22
            },
            json.loads(result.output))

    def test_list(self):
        result = self.run_command(['subnet',  'list'])
        self.assert_no_fail(result)
