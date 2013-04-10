"""
    SoftLayer.DNS
    ~~~~~~~~~~~~~
    DNS Manager/helpers

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from time import strftime
from SoftLayer.exceptions import SoftLayerError


__all__ = ["DNSZoneNotFound", "DNSManager"]


class DNSZoneNotFound(SoftLayerError):
    pass


class DNSManager(object):
    """ Manage DNS zones. """

    def __init__(self, client):
        """ DNSManager initialization.

        :param SoftLayer.API.Client client: the client instance

        """
        self.client = client
        self.domain = self.client['Dns_Domain']
        self.record = self.client['Dns_Domain_ResourceRecord']

    def list_zones(self, **kwargs):
        """ Retrieve a list of all DNS zones.

        :param dict \*\*kwargs: response-level arguments (limit, offset, etc.)

        """
        return self.client['Account'].getDomains(**kwargs)

    def get_zone(self, domain):
        """ Get a domain/zone and its records.

        :param domain: the domain/zone name

        """
        domain = domain.lower()
        results = self.domain.getByDomainName(
            domain,
            mask={'resourceRecords': {}})
        matches = filter(lambda x: x['name'].lower() == domain, results)

        try:
            return matches[0]
        except IndexError:
            raise DNSZoneNotFound(domain)

    def create_zone(self, domain, serial=None):
        """ Create a zone for the specified domain.

        :param domain: the domain/zone name to create
        :param serial: serial value on the zone (default: strftime(%Y%m%d01))

        """
        return self.domain.createObject({
            'name': domain,
            'serial': serial or strftime('%Y%m%d01')})

    def delete_zone(self, id):
        """ Delete a zone by its ID.

        :param integer id: the zone ID to delete

        """
        return self.domain.deleteObject(id=id)

    def edit_zone(self, zone):
        """ Update an existing zone with the options provided. The provided
        dict must include an 'id' key and value corresponding to the zone that
        should be updated.

        :param dict zone: the zone to update

        """
        self.domain.editObject(zone)

    def create_record(self, id, record, type, data, ttl=60):
        """ Create a resource record on a domain.

        :param integer id: the domain's ID
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

    def search_record(self, domain, record):
        """ Search for records on a domain that match a specific name.
        Useful for validating whether a record exists or that it has the
        correct value.

        :param domain: the domain/zone name in which to search.
        :param record: the record name to search for

        """
        rrs = self.get_zone(domain)['resourceRecords']
        records = filter(lambda x: x['host'].lower() == record.lower(), rrs)
        return records

    def edit_record(self, record):
        """ Update an existing record with the options provided. The provided
        dict must include an 'id' key and value corresponding to the record
        that should be updated.

        :param dict record: the record to update

        """
        self.record.editObject(record, id=record['id'])

    def dump_zone(self, id):
        """ Retrieve a zone dump in BIND format.

        :param integer id: The zone/domain ID to dump

        """
        return self.domain.getZoneFileContents(id=id)
