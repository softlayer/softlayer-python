"""
    SoftLayer.testing.fixture_client
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
# Disable pylint import error because mock might not be installed.
# Also disable the too-few-public-methods error.
# pylint: disable=F0401,R0903
import importlib

import mock


class FixtureClient(mock.MagicMixin):
    """ Implements an interface similiar to SoftLayer.Client() """

    def __init__(self):
        # Keep track of Service instances in order to do future assertions
        self.loaded_services = {}

    def __getitem__(self, service_name):
        if service_name in self.loaded_services:
            return self.loaded_services[service_name]

        service = FixtureService(service_name)
        self.loaded_services[service_name] = service

        return service

    def reset_mock(self):
        """ Reset all of the loaded mocks """
        self.loaded_services = {}


class FixtureService(mock.MagicMixin):
    """ Implements an interface similiar to SoftLayer.Service() """

    def __init__(self, service_name):
        self.service_name = service_name
        try:
            module_path = 'SoftLayer.testing.fixtures.%s' % service_name
            self.module = importlib.import_module(module_path)
        except ImportError:
            raise NotImplementedError('%s fixture is not implemented'
                                      % service_name)

        # Keep track of MagicMock instances in order to do future assertions
        self.loaded_methods = {}

    def __getattr__(self, name):
        if name in self.loaded_methods:
            return self.loaded_methods[name]

        call_handler = mock.MagicMock()
        fixture = getattr(self.module, name, None)
        if fixture is not None:
            call_handler.return_value = fixture
        else:
            raise NotImplementedError('%s::%s fixture is not implemented'
                                      % (self.service_name, name))

        self.loaded_methods[name] = call_handler
        return call_handler
