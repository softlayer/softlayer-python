"""
    SoftLayer.tests.CLI.modules.import_test
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.CLI import modules
from SoftLayer import testing

import importlib


class TestImportCLIModules(testing.TestCase):

    def test_import_all(self):
        _modules = modules.get_module_list()
        for module in _modules:
            module_path = 'SoftLayer.CLI.modules.' + module
            print("Importing %s" % module_path)
            importlib.import_module(module_path)
