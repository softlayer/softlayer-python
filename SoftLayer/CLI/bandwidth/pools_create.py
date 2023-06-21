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

regions = ['SJC/DAL/WDC/TOR/MON', 'AMS/LON/MAD/PAR', 'SNG/HKG/OSA/TOK', 'SYD', 'MEX', 'SAO', 'CHE', 'MIL', 'SEO', 'FRA']
HELP_STMT = "Ex: 'HKG' or 'SNG/HKG/OSA/TOK'"


def check_region_param(ctx, param, value):
    """Check if provided region is region group or part of region"""

    # :params string value: Region or Region-Groups
    # return string Region-Groups

    _ = [ctx, param]
    region_group = None
    for key in location_groups:
        if value in key or value is key:
            region_group = key
        else:
            continue

    if region_group:
        return region_group
    else:
        raise click.BadParameter(f"{value} is not a region or part of any \
                                 region. \nAvailable Choices: \033[1;32m{regions}")


@click.command(cls=SLCommand)
@click.option('--name', required=True, help="Pool name")
@click.option('--region', required=True,
              help=f"Choose Region/Region-Group {regions}", callback=check_region_param)
@click.help_option('--help', '-h', help=f"Specify Region or Region group - \033[1;32m{HELP_STMT}")
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
