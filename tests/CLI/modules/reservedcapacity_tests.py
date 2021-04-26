"""
    SoftLayer.tests.CLI.modules.server_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This is a series of integration tests designed to test the complete
    command line interface.

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer import testing


class ReservedCapacityCLITests(testing.TestCase):

    def test_reserved_capacity_detail(self):
        result = self.run_command(['reserved-capacity', 'detail', '100'])

        self.assert_no_fail(result)

    def test_reserved_capacity_vs_instances(self):
        result = self.run_command(['reserved-capacity', 'vs-instances', '100'])

        self.assert_no_fail(result)

    def test_reserved_capacity_guests_empty(self):
        mock = self.set_mock('SoftLayer_Virtual_ReservedCapacityGroup', 'getInstances')
        mock.return_value = [
            {
                "createDate": "2018-10-05T10:25:01-06:00",
                "guestId": 1111,
                "id": 1234,
                "reservedCapacityGroup": {
                    "accountId": 1234567,
                    "id": 111,
                    "name": "ajcbSlcliTestB1_2X8_3_YEAR_TERM",
                    "instancesCount": 1
                }
            }
        ]

        result = self.run_command(['reserved-capacity', 'vs-instances', '100'])
        self.assert_no_fail(result)

    def test_reserved_capacity_edit(self):
        mock = self.set_mock('SoftLayer_Virtual_ReservedCapacityGroup', 'editObject')
        mock.return_value = True

        result = self.run_command(['reserved-capacity', 'edit', '--name=test', '100'])
        self.assert_no_fail(result)
        self.assertEqual('The Reserved Capacity 100 was edited successfully\n', result.output)
        self.assert_called_with('SoftLayer_Virtual_ReservedCapacityGroup', 'editObject')

    def test_reserved_capacity_edit_fail(self):
        mock = self.set_mock('SoftLayer_Virtual_ReservedCapacityGroup', 'editObject')
        mock.return_value = False

        result = self.run_command(['reserved-capacity', 'edit', '--name=test', '100'])
        self.assert_no_fail(result)
        self.assertEqual('Failed to edit the Reserved Capacity 100\n', result.output)
        self.assert_called_with('SoftLayer_Virtual_ReservedCapacityGroup', 'editObject')
