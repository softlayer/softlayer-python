"""
    SoftLayer.tests.basic_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Tests shared code

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

import SoftLayer


class TestExceptions(unittest.TestCase):
    def test_softlayer_api_error(self):
        e = SoftLayer.SoftLayerAPIError('fault code', 'fault string')
        self.assertEquals(e.faultCode, 'fault code')
        self.assertEquals(e.faultString, 'fault string')
        self.assertEquals(e.reason, 'fault string')
        self.assertEquals(
            repr(e), "<SoftLayerAPIError(fault code): fault string>")
        self.assertEquals(
            str(e), "SoftLayerAPIError(fault code): fault string")

    def test_parse_error(self):
        e = SoftLayer.ParseError('fault code', 'fault string')
        self.assertEquals(e.faultCode, 'fault code')
        self.assertEquals(e.faultString, 'fault string')
        self.assertEquals(e.reason, 'fault string')
        self.assertEquals(
            repr(e), "<ParseError(fault code): fault string>")
        self.assertEquals(
            str(e), "ParseError(fault code): fault string")
