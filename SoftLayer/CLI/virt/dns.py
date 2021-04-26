"""Sync DNS records."""
# :license: MIT, see LICENSE for more details.
# pylint: disable=duplicate-code

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
@click.option('--a-record', '-a', is_flag=True, help="Sync the A record for the host")
@click.option('--aaaa-record', is_flag=True, help="Sync the AAAA record for the host")
@click.option('--ptr', is_flag=True, help="Sync the PTR record for the host")
@click.option('--ttl', default=7200, show_default=True, type=click.INT,
              help="Sets the TTL for the A and/or PTR records")
@environment.pass_env
def cli(env, identifier, a_record, aaaa_record, ptr, ttl):
    """Sync DNS records."""

    mask = """mask[id, globalIdentifier, fullyQualifiedDomainName, hostname, domain,
              primaryBackendIpAddress,primaryIpAddress,
              primaryNetworkComponent[id,primaryIpAddress,primaryVersion6IpAddressRecord[ipAddress]]]"""
    dns = SoftLayer.DNSManager(env.client)
    server = SoftLayer.VSManager(env.client)

    server_id = helpers.resolve_id(server.resolve_ids, identifier, 'VS')
    instance = server.get_instance(server_id, mask=mask)
    zone_id = helpers.resolve_id(dns.resolve_ids, instance['domain'], name='zone')

    if not instance['primaryIpAddress']:
        raise exceptions.CLIAbort('No primary IP address associated with this VS')

    go_for_it = env.skip_confirmations or formatting.confirm(
        "Attempt to update DNS records for %s" % instance['fullyQualifiedDomainName'])

    if not go_for_it:
        raise exceptions.CLIAbort("Aborting DNS sync")

    # both will be true only if no options are passed in, basically.
    both = (not ptr) and (not a_record) and (not aaaa_record)

    if both or a_record:
        dns.sync_host_record(zone_id, instance['hostname'], instance['primaryIpAddress'], 'a', ttl)

    if both or ptr:
        # getReverseDomainRecords returns a list of 1 element, so just get the top.
        ptr_domains = env.client['Virtual_Guest'].getReverseDomainRecords(id=instance['id']).pop()
        dns.sync_ptr_record(ptr_domains, instance['primaryIpAddress'], instance['fullyQualifiedDomainName'], ttl)

    if aaaa_record:
        try:
            # done this way to stay within 80 character lines
            ipv6 = instance['primaryNetworkComponent']['primaryVersion6IpAddressRecord']['ipAddress']
            dns.sync_host_record(zone_id, instance['hostname'], ipv6, 'aaaa', ttl)
        except KeyError as ex:
            message = "{} does not have an ipv6 address".format(instance['fullyQualifiedDomainName'])
            raise exceptions.CLIAbort(message) from ex
