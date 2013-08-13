from tests.mocks import hardware_mock
from mock import MagicMock


def getHardware_Mock(ids=None):
    if ids and not type(ids) is list:
        ids = [ids]

    mock = MagicMock()
    hardware_list = hardware_mock.get_raw_hardware_mocks()

    if ids:
        return_values = []
        for hw_id, hardware in hardware_list.iteritems():
            if hw_id in ids:
                return_values.append(hardware)
        mock.return_value = return_values
    else:
        mock.return_value = hardware_list.values()

    return mock
