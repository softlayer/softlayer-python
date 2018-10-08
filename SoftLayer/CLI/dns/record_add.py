"""Add resource record."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers
# pylint: disable=redefined-builtin


@click.command()
@click.argument('record')
@click.argument('record_type')
@click.argument('data')
@click.option('--zone',
              help="Zone name or identifier that the resource record will be associated with.\n"
                   "Required for all record types except PTR")
@click.option('--ttl',
              default=900,
              show_default=True,
              help='TTL value in seconds, such as 86400')
@click.option('--priority',
              default=10,
              show_default=True,
              help='The priority of the target host. (MX or SRV type only)')
@click.option('--protocol',
              type=click.Choice(['tcp', 'udp', 'tls']),
              default='tcp',
              show_default=True,
              help='The protocol of the service, usually either TCP or UDP. (SRV type only)')
@click.option('--port',
              type=click.INT,
              help='The TCP/UDP/TLS port on which the service is to be found. (SRV type only)')
@click.option('--service',
              help='The symbolic name of the desired service. (SRV type only)')
@click.option('--weight',
              default=5,
              show_default=True,
              help='Relative weight for records with same priority. (SRV type only)')
@environment.pass_env
def cli(env, record, record_type, data, zone, ttl, priority, protocol, port, service, weight):
    """Add resource record.

    Each resource record contains a RECORD and DATA property, defining a resource's name and it's target data.
    Domains contain multiple types of resource records so it can take one of the following values: A, AAAA, CNAME,
    MX, SPF, SRV, and PTR.

    About reverse records (PTR), the RECORD value must to be the public Ip Address of device you would like to manage
    reverse DNS.

        slcli dns record-add 10.10.8.21 PTR myhost.com --ttl=900

    Examples:

        slcli dns record-add myhost.com A 192.168.1.10 --zone=foobar.com --ttl=900

        slcli dns record-add myhost.com AAAA 2001:DB8::1 --zone=foobar.com

        slcli dns record-add 192.168.1.2 MX 192.168.1.10 --zone=foobar.com --priority=11 --ttl=1800

        slcli dns record-add myhost.com TXT "txt-verification=rXOxyZounZs87oacJSKvbUSIQ" --zone=2223334

        slcli dns record-add myhost.com SPF "v=spf1 include:_spf.google.com ~all" --zone=2223334

        slcli dns record-add myhost.com SRV 192.168.1.10 --zone=2223334 --service=foobar --port=80 --protocol=TCP

    """

    manager = SoftLayer.DNSManager(env.client)
    record_type = record_type.upper()

    if zone and record_type != 'PTR':
        zone_id = helpers.resolve_id(manager.resolve_ids, zone, name='zone')

        if record_type == 'MX':
            manager.create_record_mx(zone_id, record, data, ttl=ttl, priority=priority)
        elif record_type == 'SRV':
            manager.create_record_srv(zone_id, record, data, protocol, port, service,
                                      ttl=ttl, priority=priority, weight=weight)
        else:
            manager.create_record(zone_id, record, record_type, data, ttl=ttl)

    elif record_type == 'PTR':
        manager.create_record_ptr(record, data, ttl=ttl)
    else:
        raise exceptions.CLIAbort("%s isn't a valid record type or zone is missing" % record_type)

    click.secho("%s record added successfully" % record_type, fg='green')
