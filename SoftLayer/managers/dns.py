"""
    SoftLayer.dns
    ~~~~~~~~~~~~~
    DNS Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
import time

from SoftLayer import utils


class DNSManager(utils.IdentifierMixin, object):
    """Domain Name System manager.

    :param SoftLayer.API.Client client: the client instance

    """

    def __init__(self, client):
        self.client = client
        self.service = self.client['Dns_Domain']
        self.record = self.client['Dns_Domain_ResourceRecord']
        self.resolvers = [self._get_zone_id_from_name]

    def _get_zone_id_from_name(self, name):
        """Return zone ID based on a zone."""
        results = self.client['Account'].getDomains(
            filter={"domains": {"name": utils.query_filter(name)}})
        return [x['id'] for x in results]

    def list_zones(self, **kwargs):
        """Retrieve a list of all DNS zones.

        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        :returns: A list of dictionaries representing the matching zones.

        """
        return self.client['Account'].getDomains(**kwargs)

    def get_zone(self, zone_id, records=True):
        """Get a zone and its records.

        :param zone: the zone name
        :returns: A dictionary containing a large amount of information about
                  the specified zone.

        """
        mask = None
        if records:
            mask = 'resourceRecords'
        return self.service.getObject(id=zone_id, mask=mask)

    def create_zone(self, zone, serial=None):
        """Create a zone for the specified zone.

        :param zone: the zone name to create
        :param serial: serial value on the zone (default: strftime(%Y%m%d01))

        """
        return self.service.createObject({
            'name': zone,
            'serial': serial or time.strftime('%Y%m%d01'),
            "resourceRecords": {}})

    def delete_zone(self, zone_id):
        """Delete a zone by its ID.

        :param integer zone_id: the zone ID to delete

        """
        return self.service.deleteObject(id=zone_id)

    def edit_zone(self, zone):
        """Update an existing zone with the options provided.

        The provided dict must include an 'id' key and value corresponding
        to the zone that should be updated.

        :param dict zone: the zone to update

        """
        self.service.editObject(zone)

    def create_record(self, zone_id, record, record_type, data, ttl=60):
        """Create a resource record on a domain.

        :param integer id: the zone's ID
        :param record: the name of the record to add
        :param record_type: the type of record (A, AAAA, CNAME, MX, TXT, etc.)
        :param data: the record's value
        :param integer ttl: the TTL or time-to-live value (default: 60)

        """
        return self.record.createObject({
            'domainId': zone_id,
            'ttl': ttl,
            'host': record,
            'type': record_type,
            'data': data})

    def delete_record(self, record_id):
        """Delete a resource record by its ID.

        :param integer id: the record's ID

        """
        self.record.deleteObject(id=record_id)

    def get_record(self, record_id):
        """Get a DNS record.

        :param integer id: the record's ID
        """
        return self.record.getObject(id=record_id)

    def get_records(self, zone_id, ttl=None, data=None, host=None,
                    record_type=None):
        """List, and optionally filter, records within a zone.

        :param zone: the zone name in which to search.
        :param int ttl: time in seconds
        :param str data: the records data
        :param str host: record's host
        :param str record_type: the type of record

        :returns: A list of dictionaries representing the matching records
                  within the specified zone.
        """
        _filter = utils.NestedDict()

        if ttl:
            _filter['resourceRecords']['ttl'] = utils.query_filter(ttl)

        if host:
            _filter['resourceRecords']['host'] = utils.query_filter(host)

        if data:
            _filter['resourceRecords']['data'] = utils.query_filter(data)

        if record_type:
            _filter['resourceRecords']['type'] = utils.query_filter(
                record_type.lower())

        results = self.service.getResourceRecords(
            id=zone_id,
            mask='id,expire,domainId,host,minimum,refresh,retry,'
            'mxPriority,ttl,type,data,responsiblePerson',
            filter=_filter.to_dict(),
        )

        return results

    def edit_record(self, record):
        """Update an existing record with the options provided.

        The provided dict must include an 'id' key and value corresponding to
        the record that should be updated.

        :param dict record: the record to update

        """
        self.record.editObject(record, id=record['id'])

    def dump_zone(self, zone_id):
        """Retrieve a zone dump in BIND format.

        :param integer id: The zone ID to dump

        """
        return self.service.getZoneFileContents(id=zone_id)
