getObject = {
    'bandwidthAllotmentTypeId': 2,
    'createDate': '2016-07-25T08:31:17-07:00',
    'id': 123456,
    'locationGroupId': 262,
    'name': 'MexRegion',
    'serviceProviderId': 1,
    'bareMetalInstanceCount': 0,
    'hardwareCount': 2,
    'virtualGuestCount': 0,
    'activeDetails': [
        {
            'allocationId': 48293300,
            'bandwidthAllotmentId': 309961,
            'effectiveDate': '2022-02-04T00:00:00-06:00',
            'id': 48882086,
            'serviceProviderId': 1,
            'allocation': {
                'amount': '5000',
                'id': 48293300,
            }
        },
        {
            'allocationId': 48293302,
            'bandwidthAllotmentId': 309961,
            'effectiveDate': '2022-02-04T00:00:00-06:00',
            'id': 48882088,
            'serviceProviderId': 1,
            'allocation': {
                'amount': '5000',
                'id': 48293302,
            }
        }
    ],
    'bareMetalInstances': [],
    'billingCyclePublicBandwidthUsage': {
        'amountIn': '.23642',
        'amountOut': '.05475',
        'bandwidthUsageDetailTypeId': '1',
        'trackingObject': {
            'id': 258963,
            'resourceTableId': 309961,
            'startDate': '2021-03-10T11:04:56-06:00',
        }
    },
    'hardware': [
        {
            'domain': 'test.com',
            'fullyQualifiedDomainName': 'testpooling.test.com',
            'hardwareStatusId': 5,
            'hostname': 'testpooling',
            'id': 36589,
            'manufacturerSerialNumber': 'J122Y7N',
            'provisionDate': '2022-01-24T15:17:03-06:00',
            'serialNumber': 'SL018EA8',
            'serviceProviderId': 1,
            'bandwidthAllotmentDetail': {
                'allocationId': 48293302,
                'bandwidthAllotmentId': 309961,
                'effectiveDate': '2022-02-04T00:00:00-06:00',
                'id': 48882088,
                'allocation': {
                    'amount': '5000',
                    'id': 48293302,
                }
            },
            'globalIdentifier': '36e63026-5fa1-456d-a04f-adf34e60e2f4',
            'hardwareStatus': {
                'id': 5,
                'status': 'ACTIVE'
            },
            'networkManagementIpAddress': '10.130.97.247',
            'outboundBandwidthUsage': '.02594',
            'primaryBackendIpAddress': '10.130.97.227',
            'primaryIpAddress': '169.57.4.70',
            'privateIpAddress': '10.130.97.227'
        },
        {
            'domain': 'testtest.com',
            'fullyQualifiedDomainName': 'testpooling2.test.com',
            'hardwareStatusId': 5,
            'hostname': 'testpooling2',
            'id': 25478,
            'manufacturerSerialNumber': 'J12935M',
            'notes': '',
            'provisionDate': '2022-01-24T15:44:20-06:00',
            'serialNumber': 'SL01HIIB',
            'serviceProviderId': 1,
            'bandwidthAllotmentDetail': {
                'allocationId': 48293300,
                'bandwidthAllotmentId': 309961,
                'effectiveDate': '2022-02-04T00:00:00-06:00',
                'id': 48882086,
                'serviceProviderId': 1,
                'allocation': {
                    'amount': '5000',
                    'id': 478965,
                }
            },
            'globalIdentifier': '6ea407bd-9c07-4129-9103-9fda8a9e7028',
            'hardwareStatus': {
                'id': 5,
                'status': 'ACTIVE'
            },
            'networkManagementIpAddress': '10.130.97.252',
            'outboundBandwidthUsage': '.02884',
            'primaryBackendIpAddress': '10.130.97.248',
            'primaryIpAddress': '169.57.4.73',
            'privateIpAddress': '10.130.97.248'
        }
    ],
    'inboundPublicBandwidthUsage': '.23642',
    'projectedPublicBandwidthUsage': 0.43,
    'virtualGuests': [{
        'createDate': '2021-06-09T13:49:28-07:00',
        'deviceStatusId': 8,
        'domain': 'cgallo.com',
        'fullyQualifiedDomainName': 'KVM-Test.test.com',
        'hostname': 'KVM-Test',
        'id': 3578963,
        'maxCpu': 2,
        'maxCpuUnits': 'CORE',
        'maxMemory': 4096,
        'startCpus': 2,
        'statusId': 1001,
        'typeId': 1,
        'uuid': '15951561-6171-0dfc-f3d2-be039e51cc10',
        'bandwidthAllotmentDetail': {
            'allocationId': 45907006,
            'bandwidthAllotmentId': 138442,
            'effectiveDate': '2021-06-09T13:49:31-07:00',
            'id': 46467342,
            'serviceProviderId': 1,
            'allocation': {
                'amount': '0',
                'id': 45907006,
            }
        },
        'globalIdentifier': 'a245a7dd-acd1-4d1a-9356-cc1ac6b55b98',
        'outboundPublicBandwidthUsage': '.02845',
        'primaryBackendIpAddress': '10.208.73.53',
        'primaryIpAddress': '169.48.96.27',
        'status': {
            'keyName': 'ACTIVE',
            'name': 'Active'
        }
    }]
}
