"""
    SoftLayer.tests.CLI.modules.ipsec_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import json

from SoftLayer.CLI.exceptions import ArgumentError
from SoftLayer.CLI.exceptions import CLIHalt
from SoftLayer.fixtures import SoftLayer_Product_Order
from SoftLayer.fixtures import SoftLayer_Product_Package
from SoftLayer import testing
from SoftLayer import utils


class IPSECTests(testing.TestCase):

    def test_ipsec_configure(self):
        mock_account = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        mock_account.return_value = [{'id': 445}]

        mock_tunnel = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'applyConfigurationsToDevice')
        mock_tunnel.return_value = True

        result = self.run_command(['ipsec', 'configure', '445'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'applyConfigurationsToDevice',
                                identifier=445)
        self.assertEqual('Configuration request received for context #445\n',
                         result.output)

    def test_ipsec_configure_fails(self):
        mock_account = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        mock_account.return_value = [{'id': 445}]

        mock_tunnel = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'applyConfigurationsToDevice')
        mock_tunnel.return_value = False

        result = self.run_command(['ipsec', 'configure', '445'])
        self.assertIsInstance(result.exception, CLIHalt)
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'applyConfigurationsToDevice',
                                identifier=445)
        self.assertEqual(('Failed to enqueue configuration request for '
                          'context #445\n'),
                         result.output)

    def test_ipsec_detail(self):
        _mask = ('[mask[id,accountId,advancedConfigurationFlag,createDate,'
                 'customerPeerIpAddress,modifyDate,name,friendlyName,'
                 'internalPeerIpAddress,phaseOneAuthentication,'
                 'phaseOneDiffieHellmanGroup,phaseOneEncryption,'
                 'phaseOneKeylife,phaseTwoAuthentication,'
                 'phaseTwoDiffieHellmanGroup,phaseTwoEncryption,'
                 'phaseTwoKeylife,phaseTwoPerfectForwardSecrecy,presharedKey,'
                 'addressTranslations[internalIpAddressRecord[ipAddress],'
                 'customerIpAddressRecord[ipAddress]],internalSubnets,'
                 'customerSubnets,staticRouteSubnets,serviceSubnets]]')
        mock = self.set_mock('SoftLayer_Account', 'getNetworkTunnelContexts')
        mock.return_value = [{
            'id': 445,
            'name': 'der tunnel',
            'friendlyName': 'the tunnel',
            'internalPeerIpAddress': '10.0.0.1',
            'customerPeerIpAddress': '50.0.0.1',
            'advancedConfigurationFlag': 0,
            'presharedKey': 'secret',
            'phaseOneAuthentication': 'MD5',
            'phaseOneDiffieHellmanGroup': 1,
            'phaseOneEncryption': 'DES',
            'phaseOneKeylife': 600,
            'phaseTwoAuthentication': 'MD5',
            'phaseTwoDiffieHellmanGroup': 1,
            'phaseTwoEncryption': 'DES',
            'phaseTwoKeylife': 600,
            'phaseTwoPerfectForwardSecrecy': 0,
            'createDate': '2017-05-17T12:00:00-06:00',
            'modifyDate': '2017-05-17T12:01:00-06:00',
            'addressTranslations': [{
                'id': 872341,
                'internalIpAddressId': 982341,
                'internalIpAddressRecord': {'ipAddress': '10.0.0.1'},
                'customerIpAddressId': 872422,
                'customerIpAddressRecord': {'ipAddress': '50.0.0.1'},
                'notes': 'surprise!'
            }],
            'internalSubnets': [{
                'id': 324113,
                'networkIdentifier': '10.20.0.0',
                'cidr': 29,
                'note': 'Private Network'
            }],
            'customerSubnets': [{
                'id': 873411,
                'networkIdentifier': '50.0.0.0',
                'cidr': 26,
                'note': 'Offsite Network'
            }],
            'serviceSubnets': [{
                'id': 565312,
                'networkIdentifier': '100.10.0.0',
                'cidr': 26,
                'note': 'Service Network'
            }],
            'staticRouteSubnets': [{
                'id': 998232,
                'networkIdentifier': '50.50.0.0',
                'cidr': 29,
                'note': 'Static Network'
            }]
        }]
        result = self.run_command(['ipsec', 'detail', '445', '-iat', '-iis', '-irs', '-isr', '-iss'])

        split_output = []
        # Converts Rich JSON output to actual JSON data. JSON UTIL
        for table in utils.decode_stacked(result.output):
            split_output.append(table)

        self.assertEqual(6, len(split_output))
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getNetworkTunnelContexts', mask=_mask)
        self.assertEqual({'id': 445,
                          'name': 'der tunnel',
                          'friendly name': 'the tunnel',
                          'internal peer IP address': '10.0.0.1',
                          'remote peer IP address': '50.0.0.1',
                          'advanced configuration flag': 0,
                          'preshared key': 'secret',
                          'phase 1 authentication': 'MD5',
                          'phase 1 diffie hellman group': 1,
                          'phase 1 encryption': 'DES',
                          'phase 1 key life': 600,
                          'phase 2 authentication': 'MD5',
                          'phase 2 diffie hellman group': 1,
                          'phase 2 encryption': 'DES',
                          'phase 2 key life': 600,
                          'phase 2 perfect forward secrecy': 0,
                          'created': '2017-05-17T12:00:00-06:00',
                          'modified': '2017-05-17T12:01:00-06:00'},
                         split_output[0])
        self.assertEqual([{'id': 872341,
                           'remote IP address': '50.0.0.1',
                           'remote IP address id': 872422,
                           'static IP address': '10.0.0.1',
                           'static IP address id': 982341,
                           'note': 'surprise!'}],
                         split_output[1])
        self.assertEqual([{'id': 324113,
                           'network identifier': '10.20.0.0',
                           'cidr': 29,
                           'note': 'Private Network'}],
                         split_output[2])
        self.assertEqual([{'id': 873411,
                           'network identifier': '50.0.0.0',
                           'cidr': 26,
                           'note': 'Offsite Network'}],
                         split_output[3])
        self.assertEqual([{'id': 998232,
                           'network identifier': '50.50.0.0',
                           'cidr': 29,
                           'note': 'Static Network'}],
                         split_output[4])
        self.assertEqual([{'id': 565312,
                           'network identifier': '100.10.0.0',
                           'cidr': 26,
                           'note': 'Service Network'}],
                         split_output[5])

    def test_ipsec_list(self):
        mock = self.set_mock('SoftLayer_Account', 'getNetworkTunnelContexts')
        mock.return_value = [{'id': 445,
                              'name': 'der tunnel',
                              'friendlyName': 'the tunnel',
                              'internalPeerIpAddress': '10.0.0.1',
                              'customerPeerIpAddress': '50.0.0.1',
                              'advancedConfigurationFlag': 0,
                              'presharedKey': 'secret',
                              'phaseOneAuthentication': 'MD5',
                              'phaseOneDiffieHellmanGroup': 1,
                              'phaseOneEncryption': 'DES',
                              'phaseOneKeylife': 600,
                              'phaseTwoAuthentication': 'MD5',
                              'phaseTwoDiffieHellmanGroup': 1,
                              'phaseTwoEncryption': 'DES',
                              'phaseTwoKeylife': 600,
                              'phaseTwoPerfectForwardSecrecy': 0,
                              'createDate': '2017-05-17T12:00:00-06:00',
                              'modifyDate': '2017-05-17T12:01:00-06:00'}]
        result = self.run_command(['ipsec', 'list'])

        self.assert_no_fail(result)
        self.assertEqual([{
            'id': 445,
            'name': 'der tunnel',
            'friendly name': 'the tunnel',
            'internal peer IP address': '10.0.0.1',
            'remote peer IP address': '50.0.0.1',
            'created': '2017-05-17T12:00:00-06:00'
        }], json.loads(result.output))

    def test_ipsec_update(self):
        account_mock = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        account_mock.return_value = [{'id': 445,
                                      'name': 'der tunnel',
                                      'friendlyName': 'the tunnel',
                                      'internalPeerIpAddress': '10.0.0.1',
                                      'customerPeerIpAddress': '50.0.0.1',
                                      'advancedConfigurationFlag': 0,
                                      'presharedKey': 'secret',
                                      'phaseOneAuthentication': 'MD5',
                                      'phaseOneDiffieHellmanGroup': 1,
                                      'phaseOneEncryption': 'DES',
                                      'phaseOneKeylife': 600,
                                      'phaseTwoAuthentication': 'MD5',
                                      'phaseTwoDiffieHellmanGroup': 1,
                                      'phaseTwoEncryption': 'DES',
                                      'phaseTwoKeylife': 600,
                                      'phaseTwoPerfectForwardSecrecy': 0}]

        tunnel_mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'editObject')
        tunnel_mock.return_value = True

        result = self.run_command(['ipsec', 'update', '445',
                                   '--friendly-name=ipsec tunnel',
                                   '--remote-peer=50.0.0.2',
                                   '--preshared-key=enigma',
                                   '--p1-auth=SHA256', '--p1-crypto=AES256',
                                   '--p1-dh=5', '--p1-key-ttl=120',
                                   '--p2-auth=SHA1', '--p2-crypto=AES192',
                                   '--p2-dh=2', '--p2-forward-secrecy=1',
                                   '--p2-key-ttl=240'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, 'Updated context #445\n')
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'editObject',
                                identifier=445,
                                args=({'id': 445,
                                       'name': 'der tunnel',
                                       'friendlyName': 'ipsec tunnel',
                                       'internalPeerIpAddress': '10.0.0.1',
                                       'customerPeerIpAddress': '50.0.0.2',
                                       'advancedConfigurationFlag': 0,
                                       'presharedKey': 'enigma',
                                       'phaseOneAuthentication': 'SHA256',
                                       'phaseOneDiffieHellmanGroup': '5',
                                       'phaseOneEncryption': 'AES256',
                                       'phaseOneKeylife': 120,
                                       'phaseTwoAuthentication': 'SHA1',
                                       'phaseTwoDiffieHellmanGroup': '2',
                                       'phaseTwoEncryption': 'AES192',
                                       'phaseTwoKeylife': 240,
                                       'phaseTwoPerfectForwardSecrecy': 1},))

    def test_ipsec_update_fails(self):
        account_mock = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        account_mock.return_value = [{'id': 445}]

        tunnel_mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'editObject')
        tunnel_mock.return_value = False

        result = self.run_command(['ipsec', 'update', '445'])
        self.assertIsInstance(result.exception, CLIHalt)
        self.assertEqual('Failed to update context #445\n', result.output)

    def test_ipsec_subnet_add_internal(self):
        account_mock = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        account_mock.return_value = [{'id': 445}]

        tunnel_mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'addPrivateSubnetToNetworkTunnel')
        tunnel_mock.return_value = True

        result = self.run_command(['ipsec', 'subnet-add', '445', '-tinternal',
                                   '-s234716'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, 'Added internal subnet #234716\n')
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'addPrivateSubnetToNetworkTunnel',
                                identifier=445,
                                args=(234716,))

    def test_ipsec_subnet_add_remote(self):
        account_mock = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        account_mock.return_value = [{'id': 445, 'accountId': 999000}]

        tunnel_mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'addCustomerSubnetToNetworkTunnel')
        tunnel_mock.return_value = True

        subnet_mock = self.set_mock('SoftLayer_Network_Customer_Subnet',
                                    'createObject')
        subnet_mock.return_value = {'id': 234716}

        result = self.run_command(['ipsec', 'subnet-add', '445', '-tremote',
                                   '-n50.0.0.0/26'])
        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         ('Created subnet 50.0.0.0/26 #234716\n'
                          'Added remote subnet #234716\n'))
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'addCustomerSubnetToNetworkTunnel',
                                identifier=445,
                                args=(234716,))
        self.assert_called_with('SoftLayer_Network_Customer_Subnet',
                                'createObject',
                                args=({'networkIdentifier': '50.0.0.0',
                                       'cidr': 26,
                                       'accountId': 999000},))

    def test_ipsec_subnet_add_service(self):
        account_mock = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        account_mock.return_value = [{'id': 445}]

        tunnel_mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'addServiceSubnetToNetworkTunnel')
        tunnel_mock.return_value = True

        result = self.run_command(['ipsec', 'subnet-add', '445', '-tservice',
                                   '-s234716'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, 'Added service subnet #234716\n')
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'addServiceSubnetToNetworkTunnel',
                                identifier=445,
                                args=(234716,))

    def test_ipsec_subnet_add_without_id_or_network(self):
        result = self.run_command(['ipsec', 'subnet-add', '445', '-tinternal'])
        self.assertIsInstance(result.exception, ArgumentError)

    def test_ipsec_subnet_add_internal_with_network(self):
        result = self.run_command(['ipsec', 'subnet-add', '445', '-tinternal',
                                   '-n50.0.0.0/26'])
        self.assertIsInstance(result.exception, ArgumentError)

    def test_ipsec_subnet_add_fails(self):
        account_mock = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        account_mock.return_value = [{'id': 445}]

        tunnel_mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'addPrivateSubnetToNetworkTunnel')
        tunnel_mock.return_value = False

        result = self.run_command(['ipsec', 'subnet-add', '445', '-tinternal',
                                   '-s234716'])
        self.assertIsInstance(result.exception, CLIHalt)
        self.assertEqual(result.output,
                         'Failed to add internal subnet #234716\n')

    def test_ipsec_subnet_remove_internal(self):
        account_mock = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        account_mock.return_value = [{'id': 445}]

        tunnel_mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'removePrivateSubnetFromNetworkTunnel')
        tunnel_mock.return_value = True

        result = self.run_command(['ipsec', 'subnet-remove', '445',
                                   '-tinternal', '-s234716'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, 'Removed internal subnet #234716\n')
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'removePrivateSubnetFromNetworkTunnel',
                                identifier=445,
                                args=(234716,))

    def test_ipsec_subnet_remove_remote(self):
        account_mock = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        account_mock.return_value = [{'id': 445}]

        tunnel_mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'removeCustomerSubnetFromNetworkTunnel')
        tunnel_mock.return_value = True

        result = self.run_command(['ipsec', 'subnet-remove', '445',
                                   '-tremote', '-s234716'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, 'Removed remote subnet #234716\n')
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'removeCustomerSubnetFromNetworkTunnel',
                                identifier=445,
                                args=(234716,))

    def test_ipsec_subnet_remove_service(self):
        account_mock = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        account_mock.return_value = [{'id': 445}]

        tunnel_mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'removeServiceSubnetFromNetworkTunnel')
        tunnel_mock.return_value = True

        result = self.run_command(['ipsec', 'subnet-remove', '445',
                                   '-tservice', '-s234716'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, 'Removed service subnet #234716\n')
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'removeServiceSubnetFromNetworkTunnel',
                                identifier=445,
                                args=(234716,))

    def test_ipsec_subnet_remove_fails(self):
        account_mock = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        account_mock.return_value = [{'id': 445}]

        tunnel_mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'removePrivateSubnetFromNetworkTunnel')
        tunnel_mock.return_value = False

        result = self.run_command(['ipsec', 'subnet-remove', '445',
                                   '-tinternal', '-s234716'])
        self.assertIsInstance(result.exception, CLIHalt)
        self.assertEqual(result.output,
                         'Failed to remove internal subnet #234716\n')

    def test_ipsec_translation_add(self):
        account_mock = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        account_mock.return_value = [{'id': 445}]

        tunnel_mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'createAddressTranslation')
        tunnel_mock.return_value = {'id': 872843}

        result = self.run_command(['ipsec', 'translation-add', '445',
                                   '-s10.50.0.0', '-r50.50.0.0', '-nlost'])
        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         ('Created translation from 10.50.0.0 to 50.50.0.0 '
                          '#872843\n'))
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'createAddressTranslation',
                                identifier=445,
                                args=({'customerIpAddress': '50.50.0.0',
                                       'internalIpAddress': '10.50.0.0',
                                       'notes': 'lost'},))

    def test_ipsec_translation_remove(self):
        account_mock = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        account_mock.return_value = [{'id': 445,
                                      'addressTranslations': [{'id': 872843}]}]

        tunnel_mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'deleteAddressTranslation')
        tunnel_mock.return_value = True

        result = self.run_command(['ipsec', 'translation-remove', '445',
                                   '-t872843'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, 'Removed translation #872843\n')
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'deleteAddressTranslation',
                                identifier=445,
                                args=(872843,))

    def test_ipsec_translation_remove_fails(self):
        account_mock = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        account_mock.return_value = [{'id': 445,
                                      'addressTranslations': [{'id': 872843}]}]

        tunnel_mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'deleteAddressTranslation')
        tunnel_mock.return_value = False

        result = self.run_command(['ipsec', 'translation-remove', '445',
                                   '-t872843'])
        self.assertIsInstance(result.exception, CLIHalt)
        self.assertEqual(result.output,
                         'Failed to remove translation #872843\n')

    def test_ipsec_translation_update(self):
        account_mock = self.set_mock('SoftLayer_Account',
                                     'getNetworkTunnelContexts')
        account_mock.return_value = [{'id': 445,
                                      'addressTranslations': [{'id': 872843}]}]

        tunnel_mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                                    'editAddressTranslation')
        tunnel_mock.return_value = {'id': 872843}

        result = self.run_command(['ipsec', 'translation-update', '445',
                                   '-t872843', '-s10.50.0.1', '-r50.50.0.1',
                                   '-nlost'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, 'Updated translation #872843\n')
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'editAddressTranslation',
                                identifier=445,
                                args=({'id': 872843,
                                       'internalIpAddress': '10.50.0.1',
                                       'customerIpAddress': '50.50.0.1',
                                       'notes': 'lost'},))

    def test_ipsec_order(self):
        _mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        _mock.return_value = SoftLayer_Product_Package.getItems_IPSEC

        order_mock = self.set_mock('SoftLayer_Product_Order', 'placeOrder')
        order_mock.return_value = SoftLayer_Product_Order.ipsec_placeOrder
        result = self.run_command(['ipsec', 'order', '-d', 'dal13'])
        self.assert_no_fail(result)

    def test_ipsec_cancel(self):
        mock = self.set_mock('SoftLayer_Account', 'getNetworkTunnelContexts')
        mock.return_value = [{
            "createDate": "2013-11-05T16:03:53-06:00",
            "id": 445,
            "internalPeerIpAddress": "184.172.127.9",
            "modifyDate": "2022-07-19T09:34:53-06:00",
            "name": "ipsec003",
            "phaseOneAuthentication": "MD5",
            "phaseOneDiffieHellmanGroup": 2,
            "phaseOneEncryption": "3DES",
            "phaseOneKeylife": 14400,
            "phaseTwoAuthentication": "MD5",
            "phaseTwoDiffieHellmanGroup": 2,
            "phaseTwoEncryption": "3DES",
            "phaseTwoKeylife": 3600,
            "phaseTwoPerfectForwardSecrecy": 1,
            "billingItem": {
                "allowCancellationFlag": 1,
                "categoryCode": "network_tunnel",
                "createDate": "2022-07-19T09:34:52-06:00",
                "cycleStartDate": "2022-08-03T23:07:43-06:00",
                "description": "IPSEC - Standard",
                "id": 977194617,
                "lastBillDate": "2022-08-03T23:07:43-06:00",
                "modifyDate": "2022-08-03T23:07:43-06:00",
                "nextBillDate": "2022-09-03T23:00:00-06:00",
                "oneTimeFee": "0",
                "orderItemId": 932515967,
                "recurringMonths": 1,
                "serviceProviderId": 1,
            }}]

        mock = self.set_mock('SoftLayer_Billing_Item', 'cancelItem')
        mock.return_value = True
        result = self.run_command(['ipsec', 'cancel', '445', '--immediate', '--reason', 'test'])
        self.assert_no_fail(result)
