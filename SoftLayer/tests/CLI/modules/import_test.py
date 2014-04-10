"""
    SoftLayer.tests.CLI.modules.import_test
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.tests import unittest
from SoftLayer.CLI.modules import get_module_list

from importlib import import_module


class TestImportCLIModules(unittest.TestCase):

    def test_import_all(self):
        modules = get_module_list()
        for module in modules:
            module_path = 'SoftLayer.CLI.modules.' + module
            print("Importing %s" % module_path)
            import_module(module_path)
