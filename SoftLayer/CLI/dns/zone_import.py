"""Import zone based off a BIND zone file."""
# :license: MIT, see LICENSE for more details.
import re

import click

import SoftLayer
from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers

RECORD_REGEX = re.compile(r"""^((?P<domain>(([\w-]+|\*)(\.)?)*|\@)?\s+
                               (?P<ttl>\d+)?\s+
                               (?P<class>\w+)?)?\s+
                               (?P<type>\w+)\s+
                               (?P<data>.*)""", re.X)
RECORD_FMT = "type={type}, record={record}, data={data}, ttl={ttl}"


@click.command(cls=SLCommand)
@click.argument('zonefile', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--dry-run', is_flag=True, help="Don't actually create records")
@environment.pass_env
def cli(env, zonefile, dry_run):
    """Import zone based off a BIND zone file."""

    manager = SoftLayer.DNSManager(env.client)
    with open(zonefile, encoding="utf-8") as zone_f:
        zone_contents = zone_f.read()

    zone, records, bad_lines = parse_zone_details(zone_contents)

    click.secho("Parsed: zone=%s" % zone)
    for record in records:
        click.secho("Parsed: %s" % RECORD_FMT.format(**record), fg="green")

    for line in bad_lines:
        click.secho("Unparsed: %s" % line, fg="yellow")

    if dry_run:
        return

    # Find zone id or create the zone if it doesn't exist
    try:
        zone_id = helpers.resolve_id(manager.resolve_ids, zone,
                                     name='zone')
    except exceptions.CLIAbort:
        zone_id = manager.create_zone(zone)['id']
        click.secho(click.style("Created: %s" % zone, fg='green'))

    # Attempt to create each record
    for record in records:
        try:
            manager.create_record(zone_id, record['record'], record['type'], record['data'], record['ttl'])

            click.secho(click.style("Created: %s" % RECORD_FMT.format(**record), fg='green'))
        except SoftLayer.SoftLayerAPIError as ex:
            click.secho(click.style("Failed: %s" % RECORD_FMT.format(**record), fg='red'))
            click.secho(click.style(str(ex), fg='red'))

    click.secho(click.style("Finished", fg='green'))


def parse_zone_details(zone_contents):
    """Parses a zone file into python data-structures."""
    records = []
    bad_lines = []
    zone_lines = [line.strip() for line in zone_contents.split('\n')]

    zone_search = re.search(r'^\$ORIGIN (?P<zone>.*)\.', zone_lines[0])
    if zone_search:
        zone = zone_search.group('zone')
    else:
        raise exceptions.ArgumentError("Invalid Zone File")

    for line in zone_lines[1:]:
        record_search = re.search(RECORD_REGEX, line)
        if record_search is None:
            bad_lines.append(line)
            continue

        name = record_search.group('domain')
        # The API requires we send a host, although bind allows a blank
        # entry. @ is the same thing as blank
        if name is None:
            name = "@"

        ttl = record_search.group('ttl')
        # we don't do anything with the class
        # domain_class = domainSearch.group('class')
        record_type = record_search.group('type').upper()
        data = record_search.group('data')

        # the dns class doesn't support weighted MX records yet, so we chomp
        # that part out.
        if record_type == "MX":
            record_search = re.search(r'(?P<weight>\d+)\s+(?P<data>.*)', data)
            data = record_search.group('data')

        # This will skip the SOA record bit. And any domain that gets
        # parsed oddly.
        if record_type == 'IN':
            bad_lines.append(line)
            continue

        records.append({
            'record': name,
            'type': record_type,
            'data': data,
            'ttl': ttl,
        })

    return zone, records, bad_lines
