"""
    SoftLayer.tests.API.cci_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import SoftLayer
import SoftLayer.hardware

try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA
from mock import MagicMock, ANY, call


class HardwareTests_unittests(unittest.TestCase):

    def setUp(self):
        self.client = MagicMock()
        self.cci = SoftLayer.HardwareManager(self.client)

    def test_list_hardware(self):
        mcall = call(mask=ANY, filter={})
        service = self.client.__getitem__()

        self.cci.list_hardware()
        service.getHardware.assert_has_calls(mcall)

    def test_list_hardware_with_filters(self):
        self.cci.list_hardware(
            hostname='hostname',
            public_ip='1.2.3.4',
            private_ip='4.3.2.1',
        )

        service = self.client.__getitem__()
        service.getHardware.assert_has_calls(call(
            filter={
                'hardware': {
                    'hostname': {'operation': '_= hostname'},
                    'primaryIpAddress': {'operation': '_= 1.2.3.4'},
                    'primaryBackendIpAddress': {'operation': '_= 4.3.2.1'}
                }},
            mask=ANY,
        ))

    def test_resolve_ids_ip(self):
        self.client.__getitem__().getHardware.return_value = [{'id': '1234'}]
        _id = self.cci._get_ids_from_ip('1.2.3.4')
        self.assertEqual(_id, ['1234'])

        self.client.__getitem__().getHardware.side_effect = \
            [[], [{'id': '4321'}]]
        _id = self.cci._get_ids_from_ip('4.3.2.1')
        self.assertEqual(_id, ['4321'])

        _id = self.cci._get_ids_from_ip('nope')
        self.assertEqual(_id, [])

    def test_resolve_ids_hostname(self):
        self.client.__getitem__().getHardware.return_value = [{'id': '1234'}]
        _id = self.cci._get_ids_from_hostname('hostname')
        self.assertEqual(_id, ['1234'])

    def test_get_instance(self):
        self.client.__getitem__().getObject.return_value = {
            'hourlyVirtualGuests': "this is unique"}
        self.cci.get_hardware(1)
        self.client.__getitem__().getObject.assert_called_once_with(
            id=1, mask=ANY)

    def test_reload(self):
        self.cci.reload(id=1)
        f = self.client.__getitem__().reloadCurrentOperatingSystemConfiguration
        f.assert_called_once_with(id=1, token='FORCE')
