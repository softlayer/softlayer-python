"""Sync DNS records"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers

import click


@click.command(epilog="""If you don't specify any
arguments, it will attempt to update both the A and PTR records. If you don't
want to update both records, you may use the -a or --ptr arguments to limit
the records updated.""")
@click.argument('identifier')
@click.option('-a', is_flag=True, help="Sync the A record for the host")
@click.option('--ptr', is_flag=True, help="Sync the PTR record for the host")
@click.option('--ttl',
              default=7200,
              type=click.INT,
              help="Sets the TTL for the A and/or PTR records")
@environment.pass_env
def cli(env, identifier, a, ptr, ttl):
    """Sync DNS records"""

    dns = SoftLayer.DNSManager(env.client)
    vsi = SoftLayer.VSManager(env.client)

    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    instance = vsi.get_instance(vs_id)
    zone_id = helpers.resolve_id(dns.resolve_ids,
                                 instance['domain'],
                                 name='zone')

    def sync_a_record():
        """ Sync A record """
        records = dns.get_records(zone_id, host=instance['hostname'])

        if not records:
            # don't have a record, lets add one to the base zone
            dns.create_record(zone['id'],
                              instance['hostname'],
                              'a',
                              instance['primaryIpAddress'],
                              ttl=ttl)
        else:
            recs = [x for x in records if x['type'].lower() == 'a']
            if len(recs) != 1:
                raise exceptions.CLIAbort("Aborting A record sync, found "
                                          "%d A record exists!" % len(recs))
            rec = recs[0]
            rec['data'] = instance['primaryIpAddress']
            rec['ttl'] = ttl
            dns.edit_record(rec)

    def sync_ptr_record():
        """ Sync PTR record """
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
    if not ptr and not a:
        both = True

    if both or a:
        sync_a_record()

    if both or ptr:
        sync_ptr_record()
