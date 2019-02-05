getAllObjects = [
    {
        'accountId': 100,
        'eventCreateDate': '2017-10-23T14:22:36.221541-05:00',
        'eventName': 'Disable Port',
        'ipAddress': '192.168.0.1',
        'label': 'test.softlayer.com',
        'metaData': '',
        'objectId': 300,
        'objectName': 'CCI',
        'traceId': '100',
        'userId': '',
        'userType': 'SYSTEM'
    },
    {
        'accountId': 100,
        'eventCreateDate': '2017-10-18T09:40:41.830338-05:00',
        'eventName': 'Security Group Rule Added',
        'ipAddress': '192.168.0.1',
        'label': 'test.softlayer.com',
        'metaData': '{"securityGroupId":"200",'
                    '"securityGroupName":"test_SG",'
                    '"networkComponentId":"100",'
                    '"networkInterfaceType":"public",'
                    '"requestId":"53d0b91d392864e062f4958",'
                    '"rules":[{"ruleId":"100",'
                    '"remoteIp":null,"remoteGroupId":null,"direction":"ingress",'
                    '"ethertype":"IPv4",'
                    '"portRangeMin":2000,"portRangeMax":2001,"protocol":"tcp"}]}',
        'objectId': 300,
        'objectName': 'CCI',
        'traceId': '59e767e9c2184',
        'userId': 400,
        'userType': 'CUSTOMER',
        'username': 'user'
    },
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
        'metaData': '{"requestId":"2abda7ca97e5a1444cae0b9",'
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
    },
    {
        'accountId': 100,
        'eventCreateDate': '2017-10-18T10:42:11.679736-05:00',
        'eventName': 'Network Component Removed from Security Group',
        'ipAddress': '192.168.0.1',
        'label': 'test_SG',
        'metaData': '{"requestId":"6b9a87a9ab8ac9a22e87a00",'
                    '"fullyQualifiedDomainName":"test.softlayer.com",'
                    '"networkComponentId":"100",'
                    '"networkInterfaceType":"public"}',
        'objectId': 700,
        'objectName': 'Security Group',
        'traceId': '59e77653a1e5f',
        'userId': 400,
        'userType': 'CUSTOMER',
        'username': 'user'
    },
    {
        'accountId': 100,
        'eventCreateDate': '2017-10-18T10:41:49.802498-05:00',
        'eventName': 'Security Group Rule(s) Added',
        'ipAddress': '192.168.0.1',
        'label': 'test_SG',
        'metaData': '{"requestId":"0a293c1c3e59e4471da6495",'
                    '"rules":[{"ruleId":"800",'
                    '"remoteIp":null,"remoteGroupId":null,"direction":"ingress",'
                    '"ethertype":"IPv4",'
                    '"portRangeMin":2000,"portRangeMax":2001,"protocol":"tcp"}]}',
        'objectId': 700,
        'objectName': 'Security Group',
        'traceId': '59e7763dc3f1c',
        'userId': 400,
        'userType': 'CUSTOMER',
        'username': 'user'
    },
    {
        'accountId': 100,
        'eventCreateDate': '2017-10-18T10:41:42.176328-05:00',
        'eventName': 'Network Component Added to Security Group',
        'ipAddress': '192.168.0.1',
        'label': 'test_SG',
        'metaData': '{"requestId":"4709e02ad42c83f80345904",'
                    '"fullyQualifiedDomainName":"test.softlayer.com",'
                    '"networkComponentId":"100",'
                    '"networkInterfaceType":"public"}',
        'objectId': 700,
        'objectName': 'Security Group',
        'traceId': '59e77636261e7',
        'userId': 400,
        'userType': 'CUSTOMER',
        'username': 'user'
    }
]

getAllEventObjectNames = [
    {
        'value': "Account"
    },
    {
        'value': "CDN"
    },
    {
        'value': "User"
    },
    {
        'value': "Bare Metal Instance"
    },
    {
        'value': "API Authentication"
    },
    {
        'value': "Server"
    },
    {
        'value': "CCI"
    },
    {
        'value': "Image"
    },
    {
        'value': "Bluemix LB"
    },
    {
        'value': "Facility"
    },
    {
        'value': "Cloud Object Storage"
    },
    {
        'value': "Security Group"
    }
]
