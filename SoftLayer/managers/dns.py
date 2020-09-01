"""
    SoftLayer.dns
    ~~~~~~~~~~~~~
    DNS Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
import time

from SoftLayer import exceptions
from SoftLayer import utils


class DNSManager(utils.IdentifierMixin, object):
    """Manage SoftLayer DNS.

    See product information here: https://www.ibm.com/cloud/dns

    :param SoftLayer.API.BaseClient client: the client instance

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
        if kwargs.get('iter') is None:
            kwargs['iter'] = True
        return self.client.call('SoftLayer_Account', 'getDomains', **kwargs)
        # return self.client['Account'].getDomains(**kwargs)

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
        :param record_type: the type of record (A, AAAA, CNAME, TXT, etc.)
        :param data: the record's value
        :param integer ttl: the TTL or time-to-live value (default: 60)

        """
        resource_record = self._generate_create_dict(record, record_type, data,
                                                     ttl, domainId=zone_id)
        return self.record.createObject(resource_record)

    def create_record_mx(self, zone_id, record, data, ttl=60, priority=10):
        """Create a mx resource record on a domain.

        :param integer id: the zone's ID
        :param record: the name of the record to add
        :param data: the record's value
        :param integer ttl: the TTL or time-to-live value (default: 60)
        :param integer priority: the priority of the target host

        """
        resource_record = self._generate_create_dict(record, 'MX', data, ttl,
                                                     domainId=zone_id, mxPriority=priority)
        return self.record.createObject(resource_record)

    def create_record_srv(self, zone_id, record, data, protocol, port, service,
                          ttl=60, priority=20, weight=10):
        """Create a resource record on a domain.

        :param integer id: the zone's ID
        :param record: the name of the record to add
        :param data: the record's value
        :param string protocol: the protocol of the service, usually either TCP or UDP.
        :param integer port: the TCP or UDP port on which the service is to be found.
        :param string service: the symbolic name of the desired service.
        :param integer ttl: the TTL or time-to-live value (default: 60)
        :param integer priority: the priority of the target host (default: 20)
        :param integer weight: relative weight for records with same priority (default: 10)

        """
        resource_record = self._generate_create_dict(record, 'SRV', data, ttl, domainId=zone_id,
                                                     priority=priority, protocol=protocol, port=port,
                                                     service=service, weight=weight)

        # The createObject won't creates SRV records unless we send the following complexType.
        resource_record['complexType'] = 'SoftLayer_Dns_Domain_ResourceRecord_SrvType'

        return self.record.createObject(resource_record)

    def create_record_ptr(self, record, data, ttl=60):
        """Create a reverse record.

        :param record: the public ip address of device for which you would like to manage reverse DNS.
        :param data: the record's value
        :param integer ttl: the TTL or time-to-live value (default: 60)

        """
        resource_record = self._generate_create_dict(record, 'PTR', data, ttl)

        return self.record.createObject(resource_record)

    @staticmethod
    def _generate_create_dict(record, record_type, data, ttl, **kwargs):
        """Returns a dict appropriate to pass into Dns_Domain_ResourceRecord::createObject"""

        # Basic dns record structure
        resource_record = {
            'host': record,
            'data': data,
            'ttl': ttl,
            'type': record_type
        }

        for (key, value) in kwargs.items():
            resource_record.setdefault(key, value)

        return resource_record

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

    def get_records(self, zone_id, ttl=None, data=None, host=None, record_type=None):
        """List, and optionally filter, records within a zone.

        :param zone: the zone name in which to search.
        :param int ttl: time in seconds
        :param str data: the records data
        :param str host: record's host
        :param str record_type: the type of record

        :returns: A list of dictionaries representing the matching records within the specified zone.
        """
        _filter = utils.NestedDict()

        if ttl:
            _filter['resourceRecords']['ttl'] = utils.query_filter(ttl)

        if host:
            _filter['resourceRecords']['host'] = utils.query_filter(host)

        if data:
            _filter['resourceRecords']['data'] = utils.query_filter(data)

        if record_type:
            _filter['resourceRecords']['type'] = utils.query_filter(record_type.lower())

        object_mask = 'id,expire,domainId,host,minimum,refresh,retry,mxPriority,ttl,type,data,responsiblePerson'
        results = self.client.call('SoftLayer_Dns_Domain', 'getResourceRecords', id=zone_id,
                                   mask=object_mask, filter=_filter.to_dict(), iter=True)
        return results

    def edit_record(self, record):
        """Update an existing record with the options provided.

        The provided dict must include an 'id' key and value corresponding to
        the record that should be updated.

        :param dict record: the record to update

        """
        record.pop('isGatewayAddress', None)
        self.record.editObject(record, id=record['id'])

    def dump_zone(self, zone_id):
        """Retrieve a zone dump in BIND format.

        :param integer id: The zone ID to dump

        """
        return self.service.getZoneFileContents(id=zone_id)

    def sync_host_record(self, zone_id, hostname, ip_address, record_type='a', ttl=7200):
        """For a given zone_id, will set hostname's A record to ip_address

        :param integer zone_id: The zone id for the domain
        :param string hostname: host part of the record
        :param string ip_address: data part of the record
        :param integer ttl: TTL for the record
        :param string record_type: 'a' or 'aaaa'
        """
        records = self.get_records(zone_id, host=hostname, record_type=record_type)
        if not records:
            # don't have a record, lets add one to the base zone
            self.create_record(zone_id, hostname, record_type, ip_address, ttl=ttl)
        else:
            if len(records) != 1:
                raise exceptions.SoftLayerError("Aborting record sync, found %d records!" % len(records))
            rec = records[0]
            rec['data'] = ip_address
            rec['ttl'] = ttl
            self.edit_record(rec)

    def sync_ptr_record(self, ptr_domains, ip_address, fqdn, ttl=7200):
        """Sync PTR record.

        :param dict ptr_domains: result from SoftLayer_Virtual_Guest.getReverseDomainRecords or
                                 SoftLayer_Hardware_Server.getReverseDomainRecords
        :param string ip_address: ip address to sync with
        :param string fqdn: Fully Qualified Domain Name
        :param integer ttl: TTL for the record
        """
        host_rec = ip_address.split('.')[-1]
        edit_ptr = None
        for ptr in ptr_domains['resourceRecords']:
            if ptr.get('host', '') == host_rec:
                ptr['ttl'] = ttl
                edit_ptr = ptr
                break

        if edit_ptr:
            edit_ptr['data'] = fqdn
            self.edit_record(edit_ptr)
        else:
            self.create_record(ptr_domains['id'], host_rec, 'ptr', fqdn, ttl=ttl)
