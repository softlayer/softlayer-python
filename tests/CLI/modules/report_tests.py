"""
    SoftLayer.tests.CLI.modules.report_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing

import json
from unittest import mock as mock

from pprint import pprint as pp


class ReportTests(testing.TestCase):
    def test_dc_closure_report(self):
        search_mock = self.set_mock('SoftLayer_Search', 'advancedSearch')
        search_mock.side_effect = [_advanced_search(), [], [], []]
        result = self.run_command(['report', 'datacenter-closures'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Pod', 'getAllObjects', filter=mock.ANY, mask=mock.ANY)
        self.assert_called_with('SoftLayer_Search', 'advancedSearch')
        json_output = json.loads(result.output)
        pp(json_output)
        self.assertEqual(5, len(json_output))
        self.assertEqual('bcr01a.ams01', json_output[0]['POD'])


def _advanced_search():
    results = [{'matchedTerms': ['primaryRouter.hostname:|fcr01a.mex01|'],
                'relevanceScore': '5.4415264',
                'resource': {'fullyQualifiedName': 'mex01.fcr01.858',
               'hardware': [{'billingItem': {'cancellationDate': None},
                             'fullyQualifiedDomainName': 'testpooling2.ibmtest.com',
                             'id': 1676221},
                            {'billingItem': {'cancellationDate': '2022-03-03T23:59:59-06:00'},
                             'fullyQualifiedDomainName': 'testpooling.ibmtest.com',
                             'id': 1534033}],
               'id': 1133383,
               'name': 'Mex-BM-Public',
               'networkSpace': 'PUBLIC',
               'privateNetworkGateways': [],
               'publicNetworkGateways': [],
               'virtualGuests': [],
               'vlanNumber': 858},
        'resourceType': 'SoftLayer_Network_Vlan'},
        {'matchedTerms': ['primaryRouter.hostname:|fcr01a.mex01|'],
         'relevanceScore': '5.4415264',
         'resource': {'fullyQualifiedName': 'mex01.fcr01.1257',
                      'hardware': [],
                      'id': 2912280,
                      'networkSpace': 'PUBLIC',
                      'privateNetworkGateways': [],
                      'publicNetworkGateways': [],
                      'virtualGuests': [{'billingItem': {'cancellationDate': None},
                                        'fullyQualifiedDomainName': 'imageTest.ibmtest.com',
                                         'id': 127270182},
                                        {'billingItem': {'cancellationDate': None},
                                        'fullyQualifiedDomainName': 'test.deleteme.com',
                                         'id': 106291032},
                                        {'billingItem': {'cancellationDate': None},
                                         'fullyQualifiedDomainName': 'testslack.test.com',
                                         'id': 127889958}],
                      'vlanNumber': 1257},
         'resourceType': 'SoftLayer_Network_Vlan'},
        {'matchedTerms': ['primaryRouter.hostname:|bcr01a.mex01|'],
         'relevanceScore': '5.003179',
         'resource': {'fullyQualifiedName': 'mex01.bcr01.1472',
                      'hardware': [],
                      'id': 2912282,
                      'networkSpace': 'PRIVATE',
                      'privateNetworkGateways': [],
                      'publicNetworkGateways': [],
                      'virtualGuests': [{'billingItem': {'cancellationDate': None},
                                        'fullyQualifiedDomainName': 'imageTest.ibmtest.com',
                                         'id': 127270182},
                                        {'billingItem': {'cancellationDate': None},
                                        'fullyQualifiedDomainName': 'test.deleteme.com',
                                         'id': 106291032},
                                        {'billingItem': {'cancellationDate': None},
                                         'fullyQualifiedDomainName': 'testslack.test.com',
                                         'id': 127889958}],
                      'vlanNumber': 1472},
         'resourceType': 'SoftLayer_Network_Vlan'},
        {'matchedTerms': ['primaryRouter.hostname:|bcr01a.mex01|'],
         'relevanceScore': '4.9517627',
         'resource': {'fullyQualifiedName': 'mex01.bcr01.1664',
                      'hardware': [{'billingItem': {'cancellationDate': '2022-03-03T23:59:59-06:00'},
                                   'fullyQualifiedDomainName': 'testpooling.ibmtest.com',
                                    'id': 1534033},
                                   {'billingItem': {'cancellationDate': None},
                                   'fullyQualifiedDomainName': 'testpooling2.ibmtest.com',
                                    'id': 1676221}],
                      'id': 3111644,
                      'name': 'testmex',
                      'networkSpace': 'PRIVATE',
                      'privateNetworkGateways': [],
                      'publicNetworkGateways': [],
                      'virtualGuests': [],
                      'vlanNumber': 1664},
         'resourceType': 'SoftLayer_Network_Vlan'},
        {'matchedTerms': ['primaryRouter.hostname:|bcr01a.mex01|'],
         'relevanceScore': '4.9517627',
         'resource': {'fullyQualifiedName': 'mex01.bcr01.1414',
                      'hardware': [],
                      'id': 2933662,
                      'name': 'test-for-trunks',
                      'networkSpace': 'PRIVATE',
                      'privateNetworkGateways': [],
                      'publicNetworkGateways': [],
                      'virtualGuests': [],
                      'vlanNumber': 1414},
         'resourceType': 'SoftLayer_Network_Vlan'}]
    return results
