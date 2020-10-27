import json

from SoftLayer import testing


class RegistrationTests(testing.TestCase):

    def test_detail(self):
        result = self.run_command(['registration', 'detail', '1536487'])
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), {
            "id": 1536487,
            "createDate": "2017-09-08T13:35:14-06:00",
            "companyName": "test example company",
            "Name": "test Example",
            "AccountId": 1472588,
            "email": "testExample@us.ibm.com",
            "officePhone": "256325874579",
            "address1": "4567 street Rd",
            "networkIdentifier": "5.153.30.24",
            "cidr": 31,
            "detailType": "DEFAULT_PERSON",
            "networkDetail": "NETWORK",
            "status": 5
        })
