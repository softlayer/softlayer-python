"""
    SoftLayer.DNS
    ~~~~~~~~~~~~~
    DNS Manager/helpers

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from time import strftime

from SoftLayer.exceptions import DNSZoneNotFound
from SoftLayer.utils import NestedDict, query_filter, IdentifierMixin


class DNSManager(IdentifierMixin, object):
    """ Manage DNS zones. """

    def __init__(self, client):
        """ DNSManager initialization.

        :param SoftLayer.API.Client client: the client instance

        """
        self.client = client
        self.service = self.client['Dns_Domain']
        self.record = self.client['Dns_Domain_ResourceRecord']
        self.resolvers = [self._get_zone_id_from_name]

    def _get_zone_id_from_name(self, name):
            results = self.client['Account'].getDomains(
                filter={"domains": {"name": query_filter(name)}})
            return [x['id'] for x in results]

    def list_zones(self, **kwargs):
        """ Retrieve a list of all DNS zones.

        :param dict \*\*kwargs: response-level arguments (limit, offset, etc.)

        """
        return self.client['Account'].getDomains(**kwargs)

    def get_zone(self, zone_id, records=True):
        """ Get a zone and its records.

        :param zone: the zone name

        """
        mask = None
        if records:
            mask = 'resourceRecords'
        results = self.service.getObject(id=zone_id, mask=mask)

        try:
            return results[0]
        except IndexError:
            raise DNSZoneNotFound(zone_id)

    def create_zone(self, zone, serial=None):
        """ Create a zone for the specified zone.

        :param zone: the zone name to create
        :param serial: serial value on the zone (default: strftime(%Y%m%d01))

        """
        return self.service.createObject({
            'name': zone,
            'serial': serial or strftime('%Y%m%d01'),
            "resourceRecords": {}})

    def delete_zone(self, id):
        """ Delete a zone by its ID.

        :param integer id: the zone ID to delete

        """
        return self.service.deleteObject(id=id)

    def edit_zone(self, zone):
        """ Update an existing zone with the options provided. The provided
        dict must include an 'id' key and value corresponding to the zone that
        should be updated.

        :param dict zone: the zone to update

        """
        self.service.editObject(zone)

    def create_record(self, zone_id, record, type, data, ttl=60):
        """ Create a resource record on a domain.

        :param integer id: the zone's ID
        :param record: the name of the record to add
        :param type: the type of record (A, AAAA, CNAME, MX, SRV, TXT, etc.)
        :param data: the record's value
        :param integer ttl: the TTL or time-to-live value (default: 60)

        """
        self.record.createObject({
            'domainId': zone_id,
            'ttl': ttl,
            'host': record,
            'type': type,
            'data': data})

    def delete_record(self, record_id):
        """ Delete a resource record by its ID.

        :param integer id: the record's ID

        """
        self.record.deleteObject(id=record_id)

    def get_records(self, zone_id, ttl=None, data=None, host=None,
                    type=None, **kwargs):
        """ List, and optionally filter, records within a zone.

        :param zone: the zone name in which to search.
        :param int ttl: optionally, time in seconds:
        :param data: optionally, the records data
        :param host: optionally, record's host
        :param type: optionally, the type of record:

        :returns list:
        """
        _filter = NestedDict()

        if ttl:
            _filter['resourceRecords']['ttl'] = query_filter(ttl)

        if host:
            _filter['resourceRecords']['host'] = query_filter(host)

        if data:
            _filter['resourceRecords']['data'] = query_filter(data)

        if type:
            _filter['resourceRecords']['type'] = query_filter(type.lower())

        results = self.service.getResourceRecords(
            id=zone_id,
            mask='id,expire,domainId,host,minimum,refresh,retry,'
            'mxPriority,ttl,type,data,responsiblePerson',
            filter=_filter.to_dict(),
        )

        return results

    def edit_record(self, record):
        """ Update an existing record with the options provided. The provided
        dict must include an 'id' key and value corresponding to the record
        that should be updated.

        :param dict record: the record to update

        """
        self.record.editObject(record, id=record['id'])

    def dump_zone(self, zone_id):
        """ Retrieve a zone dump in BIND format.

        :param integer id: The zone ID to dump

        """
        return self.service.getZoneFileContents(id=zone_id)
