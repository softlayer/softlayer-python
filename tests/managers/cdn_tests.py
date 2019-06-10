"""
    SoftLayer.tests.managers.cdn_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.managers import cdn
from SoftLayer import testing
from SoftLayer import utils


class CDNTests(testing.TestCase):

    def set_up(self):
        self.cdn_client = cdn.CDNManager(self.client)

    def test_list_accounts(self):
        self.cdn_client.list_cdn()
        self.assert_called_with('SoftLayer_Network_CdnMarketplace_Configuration_Mapping',
                                'listDomainMappings')

    def test_detail_cdn(self):
        self.cdn_client.get_cdn("12345")

        args = ("12345",)
        self.assert_called_with('SoftLayer_Network_CdnMarketplace_Configuration_Mapping',
                                'listDomainMappingByUniqueId',
                                args=args)

    def test_detail_usage_metric(self):
        self.cdn_client.get_usage_metrics(12345, days=30, frequency="aggregate")

        _start = utils.days_to_datetime(30)
        _end = utils.days_to_datetime(0)

        _start_date = utils.timestamp(_start)
        _end_date = utils.timestamp(_end)

        args = (12345,
                _start_date,
                _end_date,
                "aggregate")
        self.assert_called_with('SoftLayer_Network_CdnMarketplace_Metrics',
                                'getMappingUsageMetrics',
                                args=args)

    def test_get_origins(self):
        self.cdn_client.get_origins("12345")
        self.assert_called_with('SoftLayer_Network_CdnMarketplace_Configuration_Mapping_Path',
                                'listOriginPath')

    def test_add_origin(self):
        self.cdn_client.add_origin("12345", "10.10.10.1", "/example/videos", origin_type="server",
                                   header="test.example.com", port=80, protocol='http', optimize_for="web",
                                   cache_query="include all")

        args = ({
                    'uniqueId': "12345",
                    'origin': '10.10.10.1',
                    'path': '/example/videos',
                    'originType': 'HOST_SERVER',
                    'header': 'test.example.com',
                    'httpPort': 80,
                    'protocol': 'HTTP',
                    'performanceConfiguration': 'General web delivery',
                    'cacheKeyQueryRule': "include all"
                },)
        self.assert_called_with('SoftLayer_Network_CdnMarketplace_Configuration_Mapping_Path',
                                'createOriginPath',
                                args=args)

    def test_remove_origin(self):
        self.cdn_client.remove_origin("12345", "/example1")

        args = ("12345",
                "/example1")
        self.assert_called_with('SoftLayer_Network_CdnMarketplace_Configuration_Mapping_Path',
                                'deleteOriginPath',
                                args=args)

    def test_purge_content(self):
        self.cdn_client.purge_content("12345", "/example1")

        args = ("12345",
                "/example1")
        self.assert_called_with('SoftLayer_Network_CdnMarketplace_Configuration_Cache_Purge',
                                'createPurge',
                                args=args)
