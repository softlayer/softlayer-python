"""
    SoftLayer.tests.CLI.modules.securitygroup_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :license: MIT, see LICENSE for more details.
"""
import json

from SoftLayer import testing


class SecurityGroupTests(testing.TestCase):
    def test_list_securitygroup(self):
        result = self.run_command(['sg', 'list'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'getAllObjects')
        self.assertEqual([{'id': 100,
                           'name': 'secgroup1',
                           'description': 'Securitygroup1'},
                          {'id': 104,
                           'name': 'secgroup2',
                           'description': None},
                          {'id': 110,
                           'name': None,
                           'description': None}],
                         json.loads(result.output))

    def test_securitygroup_detail(self):
        result = self.run_command(['sg', 'detail', '100'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'getObject', identifier='100')

        priv_server_dict = {'id': 5000, 'hostname': 'test',
                            'interface': 'PRIVATE',
                            'ipAddress': '10.3.4.5'}
        pub_server_dict = {'id': 5000, 'hostname': 'test',
                           'interface': 'PUBLIC',
                           'ipAddress': '169.23.123.43'}
        self.assertEqual({'id': 100,
                          'name': 'secgroup1',
                          'description': 'Securitygroup1',
                          'rules': [{'id': 100,
                                     'direction': 'egress',
                                     'ethertype': 'IPv4',
                                     'remoteIp': None,
                                     'remoteGroupId': None,
                                     'protocol': None,
                                     'portRangeMin': None,
                                     'portRangeMax': None}],
                          'servers': [priv_server_dict,
                                      pub_server_dict]},
                         json.loads(result.output))

    def test_securitygroup_create(self):
        result = self.run_command(['sg', 'create', '--name=secgroup1',
                                   '--description=Securitygroup1'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'createObject',
                                args=({'name': 'secgroup1',
                                       'description': 'Securitygroup1'},))
        self.assertEqual({'id': 100,
                          'name': 'secgroup1',
                          'description': 'Securitygroup1',
                          'created': '2017-05-05T12:44:43-06:00'},
                         json.loads(result.output))

    def test_securitygroup_edit(self):
        result = self.run_command(['sg', 'edit', '104', '--name=foo'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'editObject',
                                identifier='104',
                                args=({'name': 'foo'},))

    def test_securitygroup_edit_fail(self):
        fixture = self.set_mock('SoftLayer_Network_SecurityGroup',
                                'editObject')
        fixture.return_value = False

        result = self.run_command(['sg', 'edit', '100',
                                   '--name=foo'])

        self.assertEqual(result.exit_code, 2)

    def test_securitygroup_delete(self):
        result = self.run_command(['sg', 'delete', '104'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'deleteObject',
                                identifier='104')

    def test_securitygroup_delete_fail(self):
        fixture = self.set_mock('SoftLayer_Network_SecurityGroup',
                                'deleteObject')
        fixture.return_value = False

        result = self.run_command(['sg', 'delete', '100'])

        self.assertEqual(result.exit_code, 2)

    def test_securitygroup_rule_list(self):
        result = self.run_command(['sg', 'rule-list', '100'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'getRules', identifier='100')
        self.assertEqual([{'id': 100,
                           'direction': 'egress',
                           'ethertype': 'IPv4',
                           'remoteIp': None,
                           'remoteGroupId': None,
                           'protocol': None,
                           'portRangeMin': None,
                           'portRangeMax': None,
                           'createDate': None,
                           'modifyDate': None}],
                         json.loads(result.output))

    def test_securitygroup_rule_add(self):
        result = self.run_command(['sg', 'rule-add', '100',
                                   '--direction=ingress'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup', 'addRules',
                                identifier='100',
                                args=([{'direction': 'ingress'}],))

    def test_securitygroup_rule_add_fail(self):
        fixture = self.set_mock('SoftLayer_Network_SecurityGroup', 'addRules')
        fixture.return_value = False

        result = self.run_command(['sg', 'rule-add', '100',
                                   '--direction=ingress'])

        self.assertEqual(result.exit_code, 2)

    def test_securitygroup_rule_edit(self):
        result = self.run_command(['sg', 'rule-edit', '100',
                                   '520', '--direction=ingress'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'editRules', identifier='100',
                                args=([{'id': '520',
                                        'direction': 'ingress'}],))

    def test_securitygroup_rule_edit_fail(self):
        fixture = self.set_mock('SoftLayer_Network_SecurityGroup', 'editRules')
        fixture.return_value = False

        result = self.run_command(['sg', 'rule-edit', '100',
                                   '520', '--direction=ingress'])

        self.assertEqual(result.exit_code, 2)

    def test_securitygroup_rule_remove(self):
        result = self.run_command(['sg', 'rule-remove', '100', '520'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'removeRules', identifier='100',
                                args=(['520'],))

    def test_securitygroup_rule_remove_fail(self):
        fixture = self.set_mock('SoftLayer_Network_SecurityGroup',
                                'removeRules')
        fixture.return_value = False

        result = self.run_command(['sg', 'rule-remove', '100', '520'])

        self.assertEqual(result.exit_code, 2)

    def test_securitygroup_interface_list(self):
        result = self.run_command(['sg', 'interface-list', '100'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'getObject', identifier='100')
        self.assertEqual([{'hostname': 'test',
                           'interface': 'PRIVATE',
                           'ipAddress': '10.3.4.5',
                           'networkComponentId': 1000,
                           'virtualServerId': 5000},
                          {'hostname': 'test',
                           'interface': 'PUBLIC',
                           'ipAddress': '169.23.123.43',
                           'networkComponentId': 1001,
                           'virtualServerId': 5000}],
                         json.loads(result.output))

    def test_securitygroup_interface_add(self):
        result = self.run_command(['sg', 'interface-add', '100',
                                   '--network-component=1000'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'attachNetworkComponents',
                                identifier='100',
                                args=(['1000'],))

    def test_securitygroup_interface_add_fail(self):
        fixture = self.set_mock('SoftLayer_Network_SecurityGroup',
                                'attachNetworkComponents')
        fixture.return_value = False

        result = self.run_command(['sg', 'interface-add', '100',
                                   '--network-component=500'])

        self.assertEqual(result.exit_code, 2)

    def test_securitygroup_interface_remove(self):
        result = self.run_command(['sg', 'interface-remove', '100',
                                   '--network-component=500'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'detachNetworkComponents',
                                identifier='100',
                                args=(['500'],))

    def test_securitygroup_interface_remove_fail(self):
        fixture = self.set_mock('SoftLayer_Network_SecurityGroup',
                                'detachNetworkComponents')
        fixture.return_value = False

        result = self.run_command(['sg', 'interface-remove', '100',
                                   '--network-component=500'])

        self.assertEqual(result.exit_code, 2)
