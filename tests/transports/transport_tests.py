"""
    SoftLayer.tests.transports.debug
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing
from SoftLayer import transports


class TestFixtureTransport(testing.TestCase):

    def set_up(self):
        self.transport = transports.FixtureTransport()

    def test_basic(self):
        req = transports.Request()
        req.service = 'SoftLayer_Account'
        req.method = 'getObject'
        resp = self.transport(req)
        self.assertEqual(resp['accountId'], 1234)

    def test_no_module(self):
        req = transports.Request()
        req.service = 'Doesnt_Exist'
        req.method = 'getObject'
        self.assertRaises(NotImplementedError, self.transport, req)

    def test_no_method(self):
        req = transports.Request()
        req.service = 'SoftLayer_Account'
        req.method = 'getObjectzzzz'
        self.assertRaises(NotImplementedError, self.transport, req)


class TestTimingTransport(testing.TestCase):

    def set_up(self):
        fixture_transport = transports.FixtureTransport()
        self.transport = transports.TimingTransport(fixture_transport)

    def test_call(self):
        req = transports.Request()
        req.service = 'SoftLayer_Account'
        req.method = 'getObject'
        resp = self.transport(req)
        self.assertEqual(resp['accountId'], 1234)

    def test_get_last_calls(self):
        req = transports.Request()
        req.service = 'SoftLayer_Account'
        req.method = 'getObject'
        resp = self.transport(req)
        self.assertEqual(resp['accountId'], 1234)
        calls = self.transport.get_last_calls()
        self.assertEqual(calls[0][0].service, 'SoftLayer_Account')

    def test_print_reproduceable(self):
        req = transports.Request()
        req.service = 'SoftLayer_Account'
        req.method = 'getObject'
        output_text = self.transport.print_reproduceable(req)
        self.assertEqual('SoftLayer_Account', output_text)
