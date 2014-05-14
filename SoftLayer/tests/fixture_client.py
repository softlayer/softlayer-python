"""
    SoftLayer.tests.fixture_client
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from mock import MagicMock, MagicMixin
from importlib import import_module


class FixtureClient(MagicMixin):

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
        self.loaded_services = {}


class FixtureService(MagicMixin):

    def __init__(self, service_name):
        self.service_name = service_name
        try:
            self.module = import_module('SoftLayer.tests.fixtures.%s'
                                        % service_name)
        except ImportError:
            raise NotImplementedError('%s fixture is not implemented'
                                      % service_name)

        # Keep track of MagicMock instances in order to do future assertions
        self.loaded_methods = {}

    def __getattr__(self, name):
        if name in self.loaded_methods:
            return self.loaded_methods[name]

        call_handler = MagicMock()
        fixture = getattr(self.module, name, None)
        if fixture is not None:
            call_handler.return_value = fixture
        else:
            raise NotImplementedError('%s::%s fixture is not implemented'
                                      % (self.service_name, name))

        self.loaded_methods[name] = call_handler
        return call_handler
