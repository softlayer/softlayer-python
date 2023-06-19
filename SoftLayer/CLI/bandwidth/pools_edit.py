"""Edit bandwidth pool."""
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
@click.argument('identifier')
@click.option('--name', required=True, help="Pool name")
@environment.pass_env
def cli(env, identifier, name):
    """Edit bandwidth pool."""

    manager = BandwidthManager(env.client)
    bandwidth_pool = manager.edit_pool(identifier, name)

    if bandwidth_pool:

        edited_pool = manager.get_bandwidth_detail(identifier)
        locations = manager.get_location_group()

        location = next(
            (location for location in locations if location['id'] == edited_pool.get('locationGroupId')), None)

        region_name = next((key for key, value in location_groups.items() if value == location.get('name')), None)

        table = formatting.KeyValueTable(['Name', 'Value'])
        table.add_row(['Id', edited_pool.get('id')])
        table.add_row(['Name Pool', name])
        table.add_row(['Region', region_name])
        table.add_row(['Created Date', utils.clean_time(edited_pool.get('createDate'))])
        env.fout(table)
