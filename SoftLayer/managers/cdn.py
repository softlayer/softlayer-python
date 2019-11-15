"""
    SoftLayer.cdn
    ~~~~~~~~~~~~~
    CDN Manager/helpers

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer import utils


class CDNManager(utils.IdentifierMixin, object):
    """Manage Content Delivery Networks in the account.

    See product information here:
    https://www.ibm.com/cloud/cdn
    https://cloud.ibm.com/docs/infrastructure/CDN?topic=CDN-about-content-delivery-networks-cdn-

    :param SoftLayer.API.BaseClient client: the client instance
    """

    def __init__(self, client):
        self.client = client
        self._start_date = None
        self._end_date = None
        self.cdn_configuration = self.client['Network_CdnMarketplace_Configuration_Mapping']
        self.cdn_path = self.client['SoftLayer_Network_CdnMarketplace_Configuration_Mapping_Path']
        self.cdn_metrics = self.client['Network_CdnMarketplace_Metrics']
        self.cdn_purge = self.client['SoftLayer_Network_CdnMarketplace_Configuration_Cache_Purge']

    def list_cdn(self, **kwargs):
        """Lists Content Delivery Networks for the active user.

        :param dict \\*\\*kwargs: header-level options (mask, limit, etc.)
        :returns: The list of CDN objects in the account
        """

        return self.cdn_configuration.listDomainMappings(**kwargs)

    def get_cdn(self, unique_id, **kwargs):
        """Retrieves the information about the CDN account object.

        :param str unique_id: The unique ID associated with the CDN.
        :param dict \\*\\*kwargs: header-level option (mask)
        :returns: The CDN object
        """

        cdn_list = self.cdn_configuration.listDomainMappingByUniqueId(unique_id, **kwargs)

        # The method listDomainMappingByUniqueId() returns an array but there is only 1 object
        return cdn_list[0]

    def get_origins(self, unique_id, **kwargs):
        """Retrieves list of origin pull mappings for a specified CDN account.

        :param str unique_id: The unique ID associated with the CDN.
        :param dict \\*\\*kwargs: header-level options (mask, limit, etc.)
        :returns: The list of origin paths in the CDN object.
        """

        return self.cdn_path.listOriginPath(unique_id, **kwargs)

    def add_origin(self, unique_id, origin, path, origin_type="server", header=None,
                   port=80, protocol='http', bucket_name=None, file_extensions=None,
                   optimize_for="web", cache_query="include all"):
        """Creates an origin path for an existing CDN.

        :param str unique_id: The unique ID associated with the CDN.
        :param str path: relative path to the domain provided, e.g. "/articles/video"
        :param str origin: ip address or hostname if origin_type=server, API endpoint for
                           your S3 object storage if origin_type=storage
        :param str origin_type: it can be 'server' or 'storage' types.
        :param str header: the edge server uses the host header to communicate with the origin.
                           It defaults to hostname. (optional)
        :param int port: the http port number (default: 80)
        :param str protocol: the protocol of the origin (default: HTTP)
        :param str bucket_name: name of the available resource
        :param str file_extensions: file extensions that can be stored in the CDN, e.g. "jpg,png"
        :param str optimize_for: performance configuration, available options: web, video, and file where:

                                    - 'web' = 'General web delivery'
                                    - 'video' = 'Video on demand optimization'
                                    - 'file' = 'Large file optimization'
        :param str cache_query: rules with the following formats: 'include-all', 'ignore-all',
                               'include: space separated query-names',
                               'ignore: space separated query-names'.'
        :return: a CDN origin path object
        """
        types = {'server': 'HOST_SERVER', 'storage': 'OBJECT_STORAGE'}
        performance_config = {
            'web': 'General web delivery',
            'video': 'Video on demand optimization',
            'file': 'Large file optimization'
        }

        new_origin = {
            'uniqueId': unique_id,
            'path': path,
            'origin': origin,
            'originType': types.get(origin_type),
            'httpPort': port,
            'protocol': protocol.upper(),
            'performanceConfiguration': performance_config.get(optimize_for, 'General web delivery'),
            'cacheKeyQueryRule': cache_query
        }

        if header:
            new_origin['header'] = header

        if types.get(origin_type) == 'OBJECT_STORAGE':
            if bucket_name:
                new_origin['bucketName'] = bucket_name

            if file_extensions:
                new_origin['fileExtension'] = file_extensions

        origin = self.cdn_path.createOriginPath(new_origin)

        # The method createOriginPath() returns an array but there is only 1 object
        return origin[0]

    def remove_origin(self, unique_id, path):
        """Removes an origin pull mapping with the given origin pull ID.

        :param str unique_id: The unique ID associated with the CDN.
        :param str path: The origin path to delete.
        :returns: A string value
        """

        return self.cdn_path.deleteOriginPath(unique_id, path)

    def purge_content(self, unique_id, path):
        """Purges a URL or path from the CDN.

        :param str unique_id: The unique ID associated with the CDN.
        :param str path: A string of url or path that should be purged.
        :returns: A Container_Network_CdnMarketplace_Configuration_Cache_Purge array object
        """

        return self.cdn_purge.createPurge(unique_id, path)

    def get_usage_metrics(self, unique_id, history=30, frequency="aggregate"):
        """Retrieves the cdn usage metrics.

        It uses the 'days' argument if start_date and end_date are None.

        :param int unique_id: The CDN uniqueId from which the usage metrics will be obtained.
        :param int history: Last N days, default days is 30.
        :param str frequency: It can be day, week, month and aggregate. The default is "aggregate".
        :returns: A Container_Network_CdnMarketplace_Metrics object
        """

        _start = utils.days_to_datetime(history)
        _end = utils.days_to_datetime(0)

        self._start_date = utils.timestamp(_start)
        self._end_date = utils.timestamp(_end)

        usage = self.cdn_metrics.getMappingUsageMetrics(unique_id, self._start_date, self._end_date, frequency)

        # The method getMappingUsageMetrics() returns an array but there is only 1 object
        return usage[0]

    @property
    def start_data(self):
        """Retrieve the cdn usage metric start date."""
        return self._start_date

    @property
    def end_date(self):
        """Retrieve the cdn usage metric end date."""
        return self._end_date
