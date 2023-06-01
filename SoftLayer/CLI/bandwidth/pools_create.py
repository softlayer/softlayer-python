"""Create bandwidth pool."""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer import BandwidthManager
from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils

location_groups = {
    "SJC/DAL/WDC/TOR/MON": "US/Canada",
    "AMS/LON/MAD/PAR": "AMS/LON/MAD/PAR",
    "SNG/HKG/OSA/TOK": "SNG/HKG/JPN",
    "SYD": "AUS",
    "MEX": "MEX",
    "SAO": "BRA",
    "CHE": "IND",
    "MIL": "ITA",
    "SEO": "KOR",
    "FRA": "FRA"
}


@click.command(cls=SLCommand)
@click.option('--name', required=True, help="Pool name")
@click.option('--region', required=True,
              type=click.Choice(['SJC/DAL/WDC/TOR/MON', 'AMS/LON/MAD/PAR', 'SNG/HKG/OSA/TOK',
                                'SYD', 'MEX', 'SAO', 'CHE', 'MIL', 'SEO', 'FRA']),
              help="Region selected")
@environment.pass_env
def cli(env, name, region):
    """Create bandwidth pool."""

    manager = BandwidthManager(env.client)
    locations = manager.get_location_group()
    id_location_group = get_id_from_location_group(locations, location_groups[region])
    created_pool = manager.create_pool(name, id_location_group)

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.add_row(['Id', created_pool.get('id')])
    table.add_row(['Name Pool', name])
    table.add_row(['Region', region])
    table.add_row(['Created Date', utils.clean_time(created_pool.get('createDate'))])
    env.fout(table)


def get_id_from_location_group(locations, name):
    """Gets the ID location group, from name"""
    for location in locations:
        if location['name'] == name:
            return location['id']

    return None
