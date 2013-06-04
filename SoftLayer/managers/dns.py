"""
    SoftLayer.DNS
    ~~~~~~~~~~~~~
    DNS Manager/helpers

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from time import strftime

from SoftLayer.exceptions import DNSZoneNotFound


class DNSManager(object):
    """ Manage DNS zones. """

    def __init__(self, client):
        """ DNSManager initialization.

        :param SoftLayer.API.Client client: the client instance

        """
        self.client = client
        self.service = self.client['Dns_Domain']
        self.record = self.client['Dns_Domain_ResourceRecord']

    def list_zones(self, **kwargs):
        """ Retrieve a list of all DNS zones.

        :param dict \*\*kwargs: response-level arguments (limit, offset, etc.)

        """
        return self.client['Account'].getDomains(**kwargs)

    def get_zone(self, zone):
        """ Get a zone and its records.

        :param zone: the zone name

        """
        zone = zone.lower()
        results = self.service.getByDomainName(
            zone,
            mask={'resourceRecords': {}})
        matches = filter(lambda x: x['name'].lower() == zone, results)

        try:
            return matches[0]
        except IndexError:
            raise DNSZoneNotFound(zone)

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

    def create_record(self, id, record, type, data, ttl=60):
        """ Create a resource record on a domain.

        :param integer id: the zone's ID
        :param record: the name of the record to add
        :param type: the type of record (A, AAAA, CNAME, MX, SRV, TXT, etc.)
        :param data: the record's value
        :param integer ttl: the TTL or time-to-live value (default: 60)

        """
        self.record.createObject({
            'domainId': id,
            'ttl': ttl,
            'host': record,
            'type': type,
            'data': data})

    def delete_record(self, recordid):
        """ Delete a resource record by its ID.

        :param integer id: the record's ID

        """
        self.record.deleteObject(id=recordid)

    def search_record(self, zone, record):
        """ Search for records on a zone that match a specific name.
        Useful for validating whether a record exists or that it has the
        correct value.

        :param zone: the zone name in which to search.
        :param record: the record name to search for

        """
        rrs = self.get_zone(zone)['resourceRecords']
        records = filter(lambda x: x['host'].lower() == record.lower(), rrs)
        return records

    def get_records(self, zone, ttl=None, data=None, host=None,
                    type=None, **kwargs):
        """ List, and optionally filter, records within a zone.

        :param zone: the zone name in which to search.
        :param int ttl: optionally, time in seconds:
        :param data: optionally, the records data
        :param host: optionally, record's host
        :param type: optionally, the type of record:

        :returns iterator:
        """
        check = []

        if ttl:
            check.append(lambda x: x['ttl'] == ttl)

        if host:
            check.append(lambda x: x['record'] == host)

        if data:
            check.append(lambda x: x['data'] == data)

        if type:
            check.append(lambda x: x['type'] == type.lower())

        try:
            results = self.service.getByDomainName(
                zone,
                mask='resourceRecords',
                )[0]['resourceRecords']
        except (IndexError, KeyError, TypeError):
            raise DNSZoneNotFound(zone)

        # Make sure all requested filters are truthful
        filter_results = lambda x: all(v(x) for v in check)

        return filter(filter_results, results)

    def edit_record(self, record):
        """ Update an existing record with the options provided. The provided
        dict must include an 'id' key and value corresponding to the record
        that should be updated.

        :param dict record: the record to update

        """
        self.record.editObject(record, id=record['id'])

    def dump_zone(self, id):
        """ Retrieve a zone dump in BIND format.

        :param integer id: The zone ID to dump

        """
        return self.service.getZoneFileContents(id=id)
