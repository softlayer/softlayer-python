getSummaryData = [
    {
        "counter": 1.44,
        "dateTime": "2019-03-04T00:00:00-06:00",
        "type": "cpu0"
    },
    {
        "counter": 1.53,
        "dateTime": "2019-03-04T00:05:00-06:00",
        "type": "cpu0"
    },
]


# Using counter > 32bit int causes unit tests to fail.
getBandwidthData = [
    {
        'counter': 37.21,
        'dateTime': '2019-05-20T23:00:00-06:00',
        'type': 'cpu0'
    },
    {
        'counter': 76.12,
        'dateTime': '2019-05-20T23:00:00-06:00',
        'type': 'cpu1'
    },
    {
        'counter': 257623973,
        'dateTime': '2019-05-20T23:00:00-06:00',
        'type': 'memory'
    },
    {
        'counter': 137118503,
        'dateTime': '2019-05-20T23:00:00-06:00',
        'type': 'memory_usage'
    },
    {
        'counter': 125888818,
        'dateTime': '2019-05-20T23:00:00-06:00',
        'type': 'privateIn_net_octet'
    },
    {
        'counter': 961037,
        'dateTime': '2019-05-20T23:00:00-06:00',
        'type': 'privateOut_net_octet'
    },
    {
        'counter': 1449885176,
        'dateTime': '2019-05-20T23:00:00-06:00',
        'type': 'publicIn_net_octet'
    },
    {
        'counter': 91803794,
        'dateTime': '2019-05-20T23:00:00-06:00',
        'type': 'publicOut_net_octet'
    }
]
