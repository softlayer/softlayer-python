"""
    SoftLayer.tests.depecated_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

import SoftLayer
import SoftLayer.API
from SoftLayer import testing


class DeprecatedAuth(SoftLayer.AuthenticationBase):
    """Auth that only implements get_headers()."""

    def get_headers(self):
        return {'deprecated': 'header'}


class APIClient(testing.TestCase):
    def set_up(self):
        self.client = SoftLayer.Client(auth=DeprecatedAuth())

    @mock.patch('SoftLayer.transports.make_xml_rpc_api_call')
    def test_simple_call(self, make_xml_rpc_api_call):
        self.client['SERVICE'].METHOD()
        make_xml_rpc_api_call.assert_called_with(
            mock.ANY, mock.ANY, mock.ANY,
            headers={'deprecated': 'header'},
            proxy=mock.ANY,
            timeout=mock.ANY,
            http_headers=mock.ANY)
