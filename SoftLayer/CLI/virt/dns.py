"""Sync DNS records."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command(epilog="""If you don't specify any
arguments, it will attempt to update both the A and PTR records. If you don't
want to update both records, you may use the -a or --ptr arguments to limit
the records updated.""")
@click.argument('identifier')
@click.option('--a-record', '-a',
              is_flag=True,
              help="Sync the A record for the host")
@click.option('--aaaa-record',
              is_flag=True,
              help="Sync the AAAA record for the host")
@click.option('--ptr', is_flag=True, help="Sync the PTR record for the host")
@click.option('--ttl',
              default=7200,
              show_default=True,
              type=click.INT,
              help="Sets the TTL for the A and/or PTR records")
@environment.pass_env
def cli(env, identifier, a_record, aaaa_record, ptr, ttl):
    """Sync DNS records."""

    items = ['id',
             'globalIdentifier',
             'fullyQualifiedDomainName',
             'hostname',
             'domain',
             'primaryBackendIpAddress',
             'primaryIpAddress',
             '''primaryNetworkComponent[
                id, primaryIpAddress,
                primaryVersion6IpAddressRecord[ipAddress]
             ]''']
    mask = "mask[%s]" % ','.join(items)
    dns = SoftLayer.DNSManager(env.client)
    vsi = SoftLayer.VSManager(env.client)

    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    instance = vsi.get_instance(vs_id, mask=mask)
    zone_id = helpers.resolve_id(dns.resolve_ids,
                                 instance['domain'],
                                 name='zone')

    def sync_a_record():
        """Sync A record."""
        records = dns.get_records(zone_id,
                                  host=instance['hostname'],
                                  record_type='a')
        if not records:
            # don't have a record, lets add one to the base zone
            dns.create_record(zone['id'],
                              instance['hostname'],
                              'a',
                              instance['primaryIpAddress'],
                              ttl=ttl)
        else:
            if len(records) != 1:
                raise exceptions.CLIAbort("Aborting A record sync, found "
                                          "%d A record exists!" % len(records))
            rec = records[0]
            rec['data'] = instance['primaryIpAddress']
            rec['ttl'] = ttl
            dns.edit_record(rec)

    def sync_aaaa_record():
        """Sync AAAA record."""
        records = dns.get_records(zone_id,
                                  host=instance['hostname'],
                                  record_type='aaaa')
        try:
            # done this way to stay within 80 character lines
            component = instance['primaryNetworkComponent']
            record = component['primaryVersion6IpAddressRecord']
            ip_address = record['ipAddress']
        except KeyError:
            raise exceptions.CLIAbort("%s does not have an ipv6 address"
                                      % instance['fullyQualifiedDomainName'])

        if not records:
            # don't have a record, lets add one to the base zone
            dns.create_record(zone['id'],
                              instance['hostname'],
                              'aaaa',
                              ip_address,
                              ttl=ttl)
        else:
            if len(records) != 1:
                raise exceptions.CLIAbort("Aborting A record sync, found "
                                          "%d A record exists!" % len(records))
            rec = records[0]
            rec['data'] = ip_address
            rec['ttl'] = ttl
            dns.edit_record(rec)

    def sync_ptr_record():
        """Sync PTR record."""
        host_rec = instance['primaryIpAddress'].split('.')[-1]
        ptr_domains = (env.client['Virtual_Guest']
                       .getReverseDomainRecords(id=instance['id'])[0])
        edit_ptr = None
        for ptr in ptr_domains['resourceRecords']:
            if ptr['host'] == host_rec:
                ptr['ttl'] = ttl
                edit_ptr = ptr
                break

        if edit_ptr:
            edit_ptr['data'] = instance['fullyQualifiedDomainName']
            dns.edit_record(edit_ptr)
        else:
            dns.create_record(ptr_domains['id'],
                              host_rec,
                              'ptr',
                              instance['fullyQualifiedDomainName'],
                              ttl=ttl)

    if not instance['primaryIpAddress']:
        raise exceptions.CLIAbort('No primary IP address associated with '
                                  'this VS')

    zone = dns.get_zone(zone_id)

    go_for_it = env.skip_confirmations or formatting.confirm(
        "Attempt to update DNS records for %s"
        % instance['fullyQualifiedDomainName'])

    if not go_for_it:
        raise exceptions.CLIAbort("Aborting DNS sync")

    both = False
    if not ptr and not a_record and not aaaa_record:
        both = True

    if both or a_record:
        sync_a_record()

    if both or ptr:
        sync_ptr_record()

    if aaaa_record:
        sync_aaaa_record()
