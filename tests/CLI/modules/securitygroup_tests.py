"""
    SoftLayer.tests.CLI.modules.securitygroup_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :license: MIT, see LICENSE for more details.
"""
import json
from unittest import mock as mock

import SoftLayer
from SoftLayer import testing


class SecurityGroupTests(testing.TestCase):
    def set_up(self):
        self.network = SoftLayer.NetworkManager(self.client)

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

        json.loads(result.output)

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup', 'addRules',
                                identifier='100',
                                args=([{'direction': 'ingress'}],))

        self.assertEqual([{"requestId": "addRules",
                                        "rules": "[{'direction': 'ingress', "
                                        "'portRangeMax': '', "
                                        "'portRangeMin': '', "
                                        "'ethertype': 'IPv4', "
                                        "'securityGroupId': 100, 'remoteGroupId': '', "
                                        "'id': 100}]"}], json.loads(result.output))

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

        self.assertEqual([{'requestId': 'editRules'}], json.loads(result.output))

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

        self.assertEqual([{'requestId': 'removeRules'}], json.loads(result.output))

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

        self.assertEqual([{'requestId': 'interfaceAdd'}], json.loads(result.output))

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

        self.assertEqual([{'requestId': 'interfaceRemove'}], json.loads(result.output))

    def test_securitygroup_interface_remove_fail(self):
        fixture = self.set_mock('SoftLayer_Network_SecurityGroup',
                                'detachNetworkComponents')
        fixture.return_value = False

        result = self.run_command(['sg', 'interface-remove', '100',
                                   '--network-component=500'])

        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.NetworkManager.get_event_logs_by_request_id')
    def test_securitygroup_get_by_request_id(self, event_mock):
        event_mock.return_value = [
            {
                'accountId': 100,
                'eventCreateDate': '2017-10-18T09:40:32.238869-05:00',
                'eventName': 'Security Group Added',
                'ipAddress': '192.168.0.1',
                'label': 'test.softlayer.com',
                'metaData': '{"securityGroupId":"200",'
                            '"securityGroupName":"test_SG",'
                            '"networkComponentId":"100",'
                            '"networkInterfaceType":"public",'
                            '"requestId":"96c9b47b9e102d2e1d81fba"}',
                'objectId': 300,
                'objectName': 'CCI',
                'traceId': '59e767e03a57e',
                'userId': 400,
                'userType': 'CUSTOMER',
                'username': 'user'
            },
            {
                'accountId': 100,
                'eventCreateDate': '2017-10-18T10:42:13.089536-05:00',
                'eventName': 'Security Group Rule(s) Removed',
                'ipAddress': '192.168.0.1',
                'label': 'test_SG',
                'metaData': '{"requestId":"96c9b47b9e102d2e1d81fba",'
                            '"rules":[{"ruleId":"800",'
                            '"remoteIp":null,"remoteGroupId":null,"direction":"ingress",'
                            '"ethertype":"IPv4",'
                            '"portRangeMin":2000,"portRangeMax":2001,"protocol":"tcp"}]}',
                'objectId': 700,
                'objectName': 'Security Group',
                'traceId': '59e7765515e28',
                'userId': 400,
                'userType': 'CUSTOMER',
                'username': 'user'
            }
        ]

        expected = [
            {
                'date': '2017-10-18T09:40:32.238869-05:00',
                'event': 'Security Group Added',
                'label': 'test.softlayer.com',
                'metadata': json.dumps(json.loads(
                        '{"networkComponentId": "100",'
                        '"networkInterfaceType": "public",'
                        '"requestId": "96c9b47b9e102d2e1d81fba",'
                        '"securityGroupId": "200",'
                        '"securityGroupName": "test_SG"}'
                ),
                    indent=4,
                    sort_keys=True
                )
            },
            {
                'date': '2017-10-18T10:42:13.089536-05:00',
                'event': 'Security Group Rule(s) Removed',
                'label': 'test_SG',
                'metadata': json.dumps(json.loads(
                        '{"requestId": "96c9b47b9e102d2e1d81fba",'
                        '"rules": [{"direction": "ingress",'
                        '"ethertype": "IPv4",'
                        '"portRangeMax": 2001,'
                        '"portRangeMin": 2000,'
                        '"protocol": "tcp",'
                        '"remoteGroupId": null,'
                        '"remoteIp": null,'
                        '"ruleId": "800"}]}'
                ),
                    indent=4,
                    sort_keys=True
                )
            }
        ]

        result = self.run_command(['sg', 'event-log', '96c9b47b9e102d2e1d81fba'])

        self.assertEqual(expected, json.loads(result.output))
