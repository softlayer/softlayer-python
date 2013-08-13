from mock import MagicMock


def getObject_Mock(hw_id):
    mock = MagicMock()

    return_values = get_raw_hardware_mocks()

    if hw_id in return_values:
        mock.return_value = return_values[hw_id]
    else:
        mock.return_value = {}

    return mock


def get_raw_hardware_mocks():
    return {
        1000: {
            'id': 1000,
            'billingItem': {'id': 6327},
            'primaryIpAddress': '10.0.1.100',
            'hostname': 'hardware-test1',
        },
        1001: {
            'id': 1001,
            'billingItem': {'id': 7112},
            'primaryIpAddress': '10.0.4.94',
            'hostname': 'hardware-test2',
        },
    }
