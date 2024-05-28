"""
    SoftLayer.testing
    ~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
# Disable pylint import error and too many methods error
# pylint: disable=invalid-name
import logging
import os.path
import unittest
from unittest import mock as mock

from click import testing

import SoftLayer
from SoftLayer.CLI import core
from SoftLayer.CLI import environment
from SoftLayer.testing import xmlrpc

FIXTURE_PATH = os.path.abspath(os.path.join(__file__, '..', '..', 'fixtures'))


class MockableTransport(object):
    """Transport which is able to mock out specific API calls."""

    def __init__(self, transport):
        self.calls = []
        self.mocked = {}
        self.transport = transport

    def __call__(self, call):
        self._record_call(call)

        key = _mock_key(call.service, call.method)
        if key in self.mocked:
            return self.mocked[key](call)

        # Fall back to another transport (usually with fixtures)
        return self.transport(call)

    def set_mock(self, service, method):
        """Create a mock and return the mock object for the specific API call.

        :param service: API service to mock
        :param method: API method to mock
        """

        _mock = mock.MagicMock()
        self.mocked[_mock_key(service, method)] = _mock
        return _mock

    def clear(self):
        """Clear out mocks and call history."""
        self.calls = []
        self.mocked = {}

    def _record_call(self, call):
        """Record and log the API call (for later assertions)."""
        self.calls.append(call)

        details = []
        for prop in ['identifier',
                     'args',
                     'mask',
                     'filter',
                     'limit',
                     'offset']:
            details.append('%s=%r' % (prop, getattr(call, prop)))

        logging.info('%s::%s called; %s', call.service, call.method, '; '.join(details))


def _mock_key(service, method):
    """Key to address a mock object in MockableTransport."""
    return '%s::%s' % (service, method)


class TestCase(unittest.TestCase):
    """Testcase class with PEP-8 compatible method names."""

    @classmethod
    def setUpClass(cls):
        """Stand up fixtured/mockable XML-RPC server."""
        cls.mocks = MockableTransport(SoftLayer.FixtureTransport())
        cls.server = xmlrpc.create_test_server(cls.mocks)
        host, port = cls.server.socket.getsockname()[:2]
        cls.endpoint_url = "http://%s:%s" % (host, port)

    @classmethod
    def tearDownClass(cls):
        """Clean up the http server."""
        cls.server.shutdown()

    def set_up(self):
        """Aliased from setUp."""

    def tear_down(self):
        """Aliased from tearDown."""

    def setUp(self):  # NOQA
        unittest.TestCase.setUp(self)

        self.mocks.clear()

        transport = SoftLayer.XmlRpcTransport(endpoint_url=self.endpoint_url)
        wrapped_transport = SoftLayer.TimingTransport(transport)

        self.client = SoftLayer.BaseClient(transport=wrapped_transport)

        self.env = environment.Environment()
        self.env.client = self.client
        self.set_up()
        self.maxDiff = None

    def tearDown(self):  # NOQA
        super().tearDown()
        self.tear_down()
        self.mocks.clear()

    def calls(self, service=None, method=None, **props):
        """Return all API calls made during the current test."""

        conditions = []
        if service is not None:
            conditions.append(lambda call: call.service == service)
        if method is not None:
            conditions.append(lambda call: call.method == method)
        if props:
            conditions.append(lambda call: call_has_props(call, props))

        return [call for call in self.mocks.calls
                if all(cond(call) for cond in conditions)]

    def assert_called_with(self, service, method, **props):
        """Used to assert that API calls were called with given properties.

        Props are properties of the given transport.Request object.
        """

        if self.calls(service, method, **props):
            return

        raise AssertionError('%s::%s was not called with given properties: %s' % (service, method, props))

    def assert_not_called_with(self, service, method, **props):
        """Used to assert that API calls were NOT called with given properties.

        Props are properties of the given transport.Request object.
        """

        if self.calls(service, method, **props):
            raise AssertionError('%s::%s was called with given properties: %s' % (service, method, props))

    def assert_no_fail(self, result):
        """Fail when a failing click result has an error"""
        if result.exception:
            print(result.exception)
            raise result.exception

        self.assertEqual(result.exit_code, 0)

    def set_mock(self, service, method):
        """Set and return mock on the current client."""
        return self.mocks.set_mock(service, method)

    def run_command(self, args=None, env=None, fixtures=True, fmt='json', stdin=None):
        """A helper that runs a SoftLayer CLI command.

        This returns a click.testing.Result object.
        """
        args = args or []

        if fixtures is True:
            args.insert(0, '--demo')
        args.insert(0, '--format=%s' % fmt)

        runner = testing.CliRunner()
        return runner.invoke(core.cli, args=args, input=stdin, obj=env or self.env)

    def assertRaises(self, exception, function_callable, *args, **kwds):  # pylint: disable=arguments-differ
        """Converts testtools.assertRaises to unittest.assertRaises calls.

        testtools==2.4.0 require unittest2, which breaks pytest>=5.4.1 on skipTest.
        But switching to just using unittest breaks assertRaises because the format is slightly different.
        This basically just reformats the call so I don't have to re-write a bunch of tests.
        """
        with super().assertRaises(exception) as cm:
            function_callable(*args, **kwds)
        return cm.exception


def call_has_props(call, props):
    """Check if a call has matching properties of a given props dictionary."""

    for prop, expected_value in props.items():
        actual_value = getattr(call, prop)
        if actual_value != expected_value:
            logging.critical(
                '%s::%s property mismatch, %s: expected=%r; actual=%r',
                call.service,
                call.method,
                prop,
                expected_value,
                actual_value)
            return False

    return True
