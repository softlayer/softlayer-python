"""
    SoftLayer.tests.CLI.modules.nas_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing

import json


class RWhoisTests(testing.TestCase):
    def test_list_nas(self):
        result = self.run_command(['nas', 'list'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{'datacenter': 'Dallas',
                           'server': '127.0.0.1',
                           'id': 1,
                           'size': 10}])
