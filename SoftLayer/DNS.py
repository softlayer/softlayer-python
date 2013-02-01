from time import strftime
from SoftLayer.exceptions import SoftLayerError


__all__ = ["DNSZoneNotFound", "DNSManager"]


class DNSZoneNotFound(SoftLayerError):
    pass


class DNSManager(object):

    def __init__(self, client):
        """ DNSManager

            :param client: SoftLayer.API.Client
        """

        self.client = client
        self.domain = self.client['Dns_Domain']
        self.record = self.client['Dns_Domain_ResourceRecord']

    def list_zones(self):
        account = self.client['Account']
        acc = account.getObject(mask='mask.domains')
        return acc['domains']

    def get_zone(self, domain):
        """ get_zone - get a domain and it's records

            domain - str"""
        domain = domain.lower()
        results = self.domain.getByDomainName(domain,
                mask={'resourceRecords': {}})
        matches = filter(lambda x: x['name'].lower() == domain, results)

        try:
            return matches[0]
        except IndexError:
            raise DNSZoneNotFound(domain)

    def create_zone(self, domain, serial=None):
        """ create_zone - create a zone using a string

            domain - str
            serial - int (default strftime(%Y%m%d01))"""
        return self.domain.createObject({'name': domain,
            'serial': serial or strftime('%Y%m%d01')})

    def delete_zone(self, domid):
        """ delete_zone - delete a zone by it's ID """
        return self.domain.deleteObject(id=domid)

    def edit_zone(self, zone):
        self.zone.editObject(zone)

    def create_record(self, domid, record, type, data, ttl=60):
        """ create_record - create a resource record on a domain

            domid - int
            record - str
            type - str (A, AAAA, MX, ...)
            data - str
            ttl = int (default 60)"""
        self.record.createObject({
            'domainId': domid,
            'ttl': ttl,
            'host': record,
            'type': type,
            'data': data})

    def delete_record(self, recordid):
        """ delete_record - delete resource record by ID"""
        self.record.deleteObject(id=recordid)

    def search_record(self, domain, record):
        """ search_record - search for all records on a domain given a specific
        name.  Good for validating records

        domain - str
        record - str"""
        rrs = self.get_zone(domain)['resourceRecords']
        records = filter(lambda x: x['host'].lower() == record.lower(), rrs)
        return records

    def edit_record(self, record):
        self.record.editObject(record, id=record['id'])

    def dump_zone(self, domid):
        """ dump_zone - get zone in BIND format"""
        return self.domain.getZoneFileContents(id=domid)
