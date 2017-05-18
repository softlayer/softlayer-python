"""
    SoftLayer.tests.CLI.custom_types_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import click

from SoftLayer.CLI.custom_types import NetworkParamType
from SoftLayer import testing


class CustomTypesTests(testing.TestCase):

    def test_network_param_convert(self):
        param = NetworkParamType()
        (ip_address, cidr) = param.convert('10.0.0.0/24', None, None)
        self.assertEqual(ip_address, '10.0.0.0')
        self.assertEqual(cidr, 24)

    def test_network_param_convert_fails(self):
        param = NetworkParamType()
        self.assertRaises(click.exceptions.BadParameter,
                          lambda: param.convert('10.0.0.0//24', None, None))
        self.assertRaises(click.exceptions.BadParameter,
                          lambda: param.convert('10.0.0.0', None, None))
        self.assertRaises(click.exceptions.BadParameter,
                          lambda: param.convert('what is it', None, None))
        self.assertRaises(click.exceptions.BadParameter,
                          lambda: param.convert('10.0.0.0/hi', None, None))
