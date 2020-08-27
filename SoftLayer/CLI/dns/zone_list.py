"""List all zones."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.utils import clean_time


@click.command()
@environment.pass_env
def cli(env):
    """List all zones."""

    manager = SoftLayer.DNSManager(env.client)
    object_mask = "mask[id,name,serial,updateDate,resourceRecordCount]"
    zones = manager.list_zones(mask=object_mask)
    table = formatting.Table(['id', 'zone', 'serial', 'updated', 'records'])
    table.align = 'l'
    for zone in zones:
        zone_serial = str(zone.get('serial'))
        zone_date = zone.get('updateDate', None)
        if zone_date is None:
            # The serial is just YYYYMMDD##, and since there is no createDate, just format it like it was one.
            zone_date = "{}-{}-{}T00:00:00-06:00".format(zone_serial[0:4], zone_serial[4:6], zone_serial[6:8])
        table.add_row([
            zone['id'],
            zone['name'],
            zone_serial,
            clean_time(zone_date),
            zone.get('resourceRecordCount', 0)
        ])

    env.fout(table)
