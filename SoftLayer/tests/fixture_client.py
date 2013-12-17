"""
    SoftLayer.tests.fixture_client
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
from mock import MagicMock
from importlib import import_module


class FixtureClient(object):

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


class FixtureService(object):

    def __init__(self, name):
        self.name = name
        try:
            self.module = import_module('SoftLayer.tests.fixtures.%s' % name)
        except ImportError:
            self.module = None

        # Keep track of MagicMock instances in order to do future assertions
        self.loaded_methods = {}

    def __getattr__(self, name):
        if name in self.loaded_methods:
            return self.loaded_methods[name]

        call_handler = MagicMock()
        fixture = getattr(self.module, name, None)
        if fixture is not None:
            call_handler.return_value = fixture

        self.loaded_methods[name] = call_handler
        return call_handler
