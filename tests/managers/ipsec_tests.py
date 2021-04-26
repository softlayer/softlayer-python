"""
    SoftLayer.tests.managers.ipsec_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from unittest.mock import MagicMock as MagicMock

import SoftLayer
from SoftLayer.exceptions import SoftLayerAPIError
from SoftLayer import testing


class IPSECTests(testing.TestCase):

    def set_up(self):
        self.ipsec = SoftLayer.IPSECManager(self.client)

    def test_add_internal_subnet(self):
        mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                             'addPrivateSubnetToNetworkTunnel')
        mock.return_value = True
        self.assertEqual(self.ipsec.add_internal_subnet(445, 565787), True)
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'addPrivateSubnetToNetworkTunnel',
                                args=(565787,),
                                identifier=445)

    def test_add_remote_subnet(self):
        mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                             'addCustomerSubnetToNetworkTunnel')
        mock.return_value = True
        self.assertEqual(self.ipsec.add_remote_subnet(445, 565787), True)
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'addCustomerSubnetToNetworkTunnel',
                                args=(565787,),
                                identifier=445)

    def test_add_service_subnet(self):
        mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                             'addServiceSubnetToNetworkTunnel')
        mock.return_value = True
        self.assertEqual(self.ipsec.add_service_subnet(445, 565787), True)
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'addServiceSubnetToNetworkTunnel',
                                args=(565787,),
                                identifier=445)

    def test_apply_configuration(self):
        mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                             'applyConfigurationsToDevice')
        mock.return_value = True
        self.assertEqual(self.ipsec.apply_configuration(445), True)
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'applyConfigurationsToDevice',
                                args=(),
                                identifier=445)

    def test_create_remote_subnet(self):
        mock = self.set_mock('SoftLayer_Network_Customer_Subnet',
                             'createObject')
        mock.return_value = {'id': 565787,
                             'networkIdentifier': '50.0.0.0',
                             'cidr': 29,
                             'accountId': 999000}
        result = self.ipsec.create_remote_subnet(999000, '50.0.0.0', 29)
        self.assertEqual(result, mock.return_value)
        self.assert_called_with('SoftLayer_Network_Customer_Subnet',
                                'createObject',
                                args=({'networkIdentifier': '50.0.0.0',
                                       'cidr': 29,
                                       'accountId': 999000},))

    def test_create_translation(self):
        mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                             'createAddressTranslation')
        mock.return_value = {'id': 787989,
                             'customerIpAddress': '50.0.0.0',
                             'customerIpAddressId': 672634,
                             'internalIpAddress': '10.0.0.0',
                             'internalIpAddressId': 871231,
                             'notes': 'first translation'}
        result = self.ipsec.create_translation(445,
                                               '10.0.0.0',
                                               '50.0.0.0',
                                               'first translation')
        self.assertEqual(result, mock.return_value)
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'createAddressTranslation',
                                args=({'customerIpAddress': '50.0.0.0',
                                       'internalIpAddress': '10.0.0.0',
                                       'notes': 'first translation'},),
                                identifier=445)

    def test_delete_remote_subnet(self):
        mock = self.set_mock('SoftLayer_Network_Customer_Subnet',
                             'deleteObject')
        mock.return_value = True
        self.assertEqual(self.ipsec.delete_remote_subnet(565787), True)
        self.assert_called_with('SoftLayer_Network_Customer_Subnet',
                                'deleteObject',
                                identifier=565787)

    def test_get_tunnel_context(self):
        _filter = {'networkTunnelContexts': {'id': {'operation': 445}}}
        _mask = '[mask[id]]'

        mock = self.set_mock('SoftLayer_Account', 'getNetworkTunnelContexts')
        mock.return_value = [{'id': 445}]
        result = self.ipsec.get_tunnel_context(445, mask=_mask)
        self.assertEqual(result, mock.return_value[0])
        self.assert_called_with('SoftLayer_Account',
                                'getNetworkTunnelContexts',
                                filter=_filter,
                                mask=_mask)

    def test_get_tunnel_context_raises_error(self):
        mock = self.set_mock('SoftLayer_Account', 'getNetworkTunnelContexts')
        mock.return_value = []
        self.assertRaises(SoftLayerAPIError,
                          self.ipsec.get_tunnel_context,
                          445)

    def test_get_translation(self):
        mock = self.set_mock('SoftLayer_Account', 'getNetworkTunnelContexts')
        mock.return_value = [{'id': 445, 'addressTranslations':
                              [{'id': 234123}, {'id': 872341}]}]
        self.assertEqual(self.ipsec.get_translation(445, 872341),
                         {'id': 872341,
                          'customerIpAddress': '',
                          'internalIpAddress': ''})
        self.assert_called_with('SoftLayer_Account',
                                'getNetworkTunnelContexts')

    def test_get_translation_raises_error(self):
        mock = self.set_mock('SoftLayer_Account', 'getNetworkTunnelContexts')
        mock.return_value = [{'id': 445, 'addressTranslations':
                              [{'id': 234123}]}]
        self.assertRaises(SoftLayerAPIError,
                          self.ipsec.get_translation,
                          445,
                          872341)

    def test_get_translations(self):
        _mask = ('[mask[addressTranslations[customerIpAddressRecord,'
                 'internalIpAddressRecord]]]')
        _filter = {'networkTunnelContexts': {'id': {'operation': 445}}}
        mock = self.set_mock('SoftLayer_Account', 'getNetworkTunnelContexts')
        mock.return_value = [{'id': 445,
                              'addressTranslations': [{
                                  'id': 234123,
                                  'customerIpAddressRecord':
                                      {'ipAddress': '50.0.0.0'},
                                  'customerIpAddressId': 234112,
                                  'internalIpAddressRecord':
                                      {'ipAddress': '10.0.0.0'},
                                  'internalIpAddressId': 234442
                              }]}]
        self.assertEqual(self.ipsec.get_translations(445),
                         [{'id': 234123,
                           'customerIpAddress': '50.0.0.0',
                           'customerIpAddressId': 234112,
                           'internalIpAddress': '10.0.0.0',
                           'internalIpAddressId': 234442}])
        self.assert_called_with('SoftLayer_Account',
                                'getNetworkTunnelContexts',
                                filter=_filter,
                                mask=_mask)

    def test_get_tunnel_contexts(self):
        _mask = '[mask[addressTranslations]]'
        mock = self.set_mock('SoftLayer_Account', 'getNetworkTunnelContexts')
        mock.return_value = [{'id': 445}, {'id': 446}]
        self.assertEqual(self.ipsec.get_tunnel_contexts(mask=_mask),
                         mock.return_value)
        self.assert_called_with('SoftLayer_Account',
                                'getNetworkTunnelContexts',
                                mask=_mask)

    def test_remove_internal_subnet(self):
        mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                             'removePrivateSubnetFromNetworkTunnel')
        mock.return_value = True
        self.assertEqual(self.ipsec.remove_internal_subnet(445, 565787), True)
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'removePrivateSubnetFromNetworkTunnel',
                                args=(565787,),
                                identifier=445)

    def test_remove_remote_subnet(self):
        mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                             'removeCustomerSubnetFromNetworkTunnel')
        mock.return_value = True
        self.assertEqual(self.ipsec.remove_remote_subnet(445, 565787), True)
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'removeCustomerSubnetFromNetworkTunnel',
                                args=(565787,),
                                identifier=445)

    def test_remove_service_subnet(self):
        mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                             'removeServiceSubnetFromNetworkTunnel')
        mock.return_value = True
        self.assertEqual(self.ipsec.remove_service_subnet(445, 565787), True)
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'removeServiceSubnetFromNetworkTunnel',
                                args=(565787,),
                                identifier=445)

    def test_remove_translation(self):
        mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                             'deleteAddressTranslation')
        mock.return_value = True
        self.assertEqual(self.ipsec.remove_translation(445, 787547), True)
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'deleteAddressTranslation',
                                args=(787547,),
                                identifier=445)

    def test_update_translation(self):
        mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                             'editAddressTranslation')
        mock.return_value = True
        translation = {'id': 234123,
                       'customerIpAddress': '50.0.0.0',
                       'customerIpAddressId': 234112,
                       'internalIpAddress': '10.0.0.0',
                       'internalIpAddressId': 234442}
        self.ipsec.get_translation = MagicMock(return_value=translation)

        result = self.ipsec.update_translation(445,
                                               234123,
                                               static_ip='10.0.0.2',
                                               remote_ip='50.0.0.2',
                                               notes='do not touch')
        self.assertEqual(result, True)
        self.ipsec.get_translation.assert_called_with(445, 234123)
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'editAddressTranslation',
                                args=({'id': 234123,
                                       'customerIpAddress': '50.0.0.2',
                                       'internalIpAddress': '10.0.0.2',
                                       'notes': 'do not touch'},),
                                identifier=445)

    def test_update_tunnel_context(self):
        mock = self.set_mock('SoftLayer_Network_Tunnel_Module_Context',
                             'editObject')
        mock.return_value = True
        context = {'id': 445,
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
                   'phaseTwoPerfectForwardSecrecy': 0}
        self.ipsec.get_tunnel_context = MagicMock(return_value=context)

        result = self.ipsec.update_tunnel_context(445,
                                                  friendly_name='ipsec tunnel',
                                                  remote_peer='50.0.0.2',
                                                  preshared_key='enigma',
                                                  phase1_auth='SHA256',
                                                  phase1_dh=5,
                                                  phase1_crypto='AES256',
                                                  phase1_key_ttl=120,
                                                  phase2_auth='SHA128',
                                                  phase2_dh=2,
                                                  phase2_crypto='AES192',
                                                  phase2_key_ttl=240,
                                                  phase2_forward_secrecy=1)
        self.assertEqual(result, True)
        self.ipsec.get_tunnel_context.assert_called_with(445)
        self.assert_called_with('SoftLayer_Network_Tunnel_Module_Context',
                                'editObject',
                                args=({'id': 445,
                                       'name': 'der tunnel',
                                       'friendlyName': 'ipsec tunnel',
                                       'internalPeerIpAddress': '10.0.0.1',
                                       'customerPeerIpAddress': '50.0.0.2',
                                       'advancedConfigurationFlag': 0,
                                       'presharedKey': 'enigma',
                                       'phaseOneAuthentication': 'SHA256',
                                       'phaseOneDiffieHellmanGroup': 5,
                                       'phaseOneEncryption': 'AES256',
                                       'phaseOneKeylife': 120,
                                       'phaseTwoAuthentication': 'SHA128',
                                       'phaseTwoDiffieHellmanGroup': 2,
                                       'phaseTwoEncryption': 'AES192',
                                       'phaseTwoKeylife': 240,
                                       'phaseTwoPerfectForwardSecrecy': 1},),
                                identifier=445)
