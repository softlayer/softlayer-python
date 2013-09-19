"""
    SoftLayer.tests.mocks.account_mock
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Mocks API calls documented at
    http://sldn.softlayer.com/reference/services/SoftLayer_Account

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.tests.mocks import hardware_mock, virtual_guest_mock
from mock import MagicMock


def getHardware_Mock(ids=None):
    if ids and not type(ids) is list:
        ids = [ids]

    mock = MagicMock()
    hardware_list = hardware_mock.get_raw_hardware_mocks()

    if ids:
        return_values = []
        for hw_id, hardware in hardware_list.items():
            if hw_id in ids:
                return_values.append(hardware)
        mock.return_value = return_values
    else:
        mock.return_value = hardware_list.values()

    return mock


def getHourlyVirtualGuests_Mock(ids=None):
    mock = getVirtualGuests_Mock(ids)

    results = []
    for cci in mock.return_value:
        if cci['hourlyBillingFlag']:
            results.append(cci)

    mock.return_value = results

    return mock


def getMonthlyVirtualGuests_Mock(ids=None):
    mock = getVirtualGuests_Mock(ids)

    results = []
    for cci in mock.return_value:
        if not cci['hourlyBillingFlag']:
            results.append(cci)

    mock.return_value = results

    return mock


def getVirtualGuests_Mock(ids=None):
    if ids and not type(ids) is list:
        ids = [ids]

    mock = MagicMock()
    cci_list = virtual_guest_mock.get_raw_cci_mocks()

    if ids:
        return_values = []
        for cci_id, cci in cci_list.items():
            if cci_id in ids:
                return_values.append(cci)
        mock.return_value = return_values
    else:
        mock.return_value = cci_list.values()

    return mock
