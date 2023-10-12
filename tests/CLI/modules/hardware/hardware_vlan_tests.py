"""
    SoftLayer.tests.CLI.modules.hardware.hardware_vlan_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    These tests are for any commands that work with the vlans on hardware objects.

    :license: MIT, see LICENSE for more details.
"""

import json
import sys
import tempfile
from unittest import mock as mock

from SoftLayer.CLI import exceptions
from SoftLayer.fixtures import SoftLayer_Hardware_Server
from SoftLayer.fixtures import SoftLayer_Search
from SoftLayer import SoftLayerError
from SoftLayer import testing
from SoftLayer import utils


class HardwareVlanCLITests(testing.TestCase):

    # slcli hardware vlan-trunkable
    def test_hardware_vlan_trunkable_no_hardware(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getNetworkComponents')
        mock.return_value = []
        result = self.run_command(['hardware', 'vlan-trunkable'])
        self.assertEqual(2, result.exit_code)
        self.assertIn("Missing argument 'HARDWARE'.", result.output)

    def test_hardware_vlan_trunkable_happypath(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getNetworkComponents')
        mock.return_value = [
            {
                'maxSpeed': 1000,
                'networkVlansTrunkable': [{
                    'id':5555,
                    'fullyQualifiedName': 'test01.ibm99.1234',
                    'name': 'IBMTEst',
                    'networkSpace': 'PUBLIC'
                }],
                'primaryIpAddress': '192.168.1.1',
                'id': 998877,
            }
        ]
        result = self.run_command(['hardware', 'vlan-trunkable', '12345'])
        self.assert_no_fail(result)
        output = json.loads(result.output)
        self.assertEqual(len(output), 1)
        self.assertEqual(output[0]['ID'], 5555)

    def test_hardware_vlan_trunkable_no_vlans(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getNetworkComponents')
        mock.return_value = []
        result = self.run_command(['--format=table', 'hardware', 'vlan-trunkable', '12345'])
        print(result.output)
        self.assert_no_fail(result)
        self.assertIn("No trunkable vlans found.", result.output)

    def test_hardware_vlan_trunkable_no_vlans_json(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getNetworkComponents')
        mock.return_value = []
        result = self.run_command(['hardware', 'vlan-trunkable', '12345'])
        output = json.loads(result.output)
        self.assert_no_fail(result)
        self.assertEqual([], output)


    # slcli hardware vlan-remove
    def test_hardware_vlan_remove(self):
        mock = self.set_mock('SoftLayer_Search', 'advancedSearch')
        mock.return_value = SoftLayer_Search.advancedSearchVlan
        result = self.run_command(['hardware', 'vlan-remove', '12345', '5555'])
        self.assert_no_fail(result)
        search_args = '_objectType:SoftLayer_Network_Vlan "5555"'
        self.assert_called_with('SoftLayer_Search', 'advancedSearch', args=(search_args,))
        self.assert_called_with('SoftLayer_Hardware_Server', 'getFrontendNetworkComponents', identifier=12345)
        self.assert_called_with('SoftLayer_Hardware_Server', 'getBackendNetworkComponents', identifier=12345)
        self.assert_called_with('SoftLayer_Network_Component', 'removeNetworkVlanTrunks', identifier=998877)
        self.assert_called_with('SoftLayer_Network_Component', 'removeNetworkVlanTrunks', identifier=123456)

    def test_hardware_vlan_remove_two_vlans(self):
        mock = self.set_mock('SoftLayer_Search', 'advancedSearch')
        mock.return_value = SoftLayer_Search.advancedSearchVlan
        result = self.run_command(['hardware', 'vlan-remove', '12345', '5555', 'testVlan'])
        self.assert_no_fail(result)
        search_args = '_objectType:SoftLayer_Network_Vlan "5555" "testVlan"'
        self.assert_called_with('SoftLayer_Search', 'advancedSearch', args=(search_args,))

    def test_hardware_vlan_remove_no_vlans(self):
        mock = self.set_mock('SoftLayer_Search', 'advancedSearch')
        mock.return_value = SoftLayer_Search.advancedSearchVlan
        result = self.run_command(['hardware', 'vlan-remove', '12345'])
        self.assertEqual(2, result.exit_code)
        self.assertEqual("Argument Error: Error: Missing argument 'VLANS'.", result.exception.message)

    def test_hardware_vlan_remove_all_vlans(self):
        from pprint import pprint as pp
        mock = self.set_mock('SoftLayer_Search', 'advancedSearch')
        mock.return_value = SoftLayer_Search.advancedSearchVlan
        hardware_mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        hardware_return = {
            'backendNetworkComponent': SoftLayer_Hardware_Server.getBackendNetworkComponents,
            'frontendNetworkComponent': SoftLayer_Hardware_Server.getFrontendNetworkComponents
        }
        hardware_return['backendNetworkComponent'][1]['networkVlanTrunks'] = [{'id': 99}]
        hardware_return['frontendNetworkComponent'][1]['networkVlanTrunks'] = [{'id': 11}]
        hardware_mock.return_value = hardware_return
        result = self.run_command(['hardware', 'vlan-remove', '12345', '--all'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Component', 'clearNetworkVlanTrunks', identifier=998877)
        self.assert_called_with('SoftLayer_Network_Component', 'clearNetworkVlanTrunks', identifier=123456)

    # slcli hardware vlan-add
    def test_hardware_vlan_add(self):
        mock = self.set_mock('SoftLayer_Search', 'advancedSearch')
        mock.return_value = SoftLayer_Search.advancedSearchVlan
        result = self.run_command(['hardware', 'vlan-add', '12345', '5555'])
        self.assert_no_fail(result)
        search_args = '_objectType:SoftLayer_Network_Vlan "5555"'
        self.assert_called_with('SoftLayer_Search', 'advancedSearch', args=(search_args,))
        self.assert_called_with('SoftLayer_Hardware_Server', 'getFrontendNetworkComponents', identifier=12345)
        self.assert_called_with('SoftLayer_Hardware_Server', 'getBackendNetworkComponents', identifier=12345)
        self.assert_called_with('SoftLayer_Network_Component', 'addNetworkVlanTrunks', identifier=998877)
        self.assert_called_with('SoftLayer_Network_Component', 'addNetworkVlanTrunks', identifier=123456)

    def test_hardware_vlan_add_two_vlans(self):
        mock = self.set_mock('SoftLayer_Search', 'advancedSearch')
        mock.return_value = SoftLayer_Search.advancedSearchVlan
        result = self.run_command(['hardware', 'vlan-add', '12345', '5555', 'testVlan'])
        self.assert_no_fail(result)
        search_args = '_objectType:SoftLayer_Network_Vlan "5555" "testVlan"'
        self.assert_called_with('SoftLayer_Search', 'advancedSearch', args=(search_args,))

    def test_hardware_vlan_add_no_vlans(self):
        mock = self.set_mock('SoftLayer_Search', 'advancedSearch')
        mock.return_value = SoftLayer_Search.advancedSearchVlan
        result = self.run_command(['hardware', 'vlan-add', '12345'])
        self.assertEqual(2, result.exit_code)
        self.assertEqual("Argument Error: Error: Missing argument 'VLANS'.", result.exception.message)