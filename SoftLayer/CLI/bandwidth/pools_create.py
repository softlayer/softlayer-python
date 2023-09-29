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


def check_region_param(ctx, param, value):  # pylint: disable=unused-argument
    """Check if provided region is region group or part of region

    :params string value: Region or Region-Groups
    return string Region-Groups
    """

    region_group = None
    for key in location_groups:
        if value in key or value is key:
            region_group = key

    if region_group:
        return region_group
    else:
        raise click.BadParameter(f"{value} is not a region or part of any region."
                                 " Available Choices: ['SJC/DAL/WDC/TOR/MON', 'AMS/LON/MAD/PAR',"
                                 " 'SNG/HKG/OSA/TOK', 'SYD', 'MEX', 'SAO', 'CHE', 'MIL', 'SEO', 'FRA']")


@click.command(cls=SLCommand)
@click.option('--name', required=True, help="Pool name")
@click.option('--region', required=True,
              help=f"Choose Region/Region-Group {regions}", callback=check_region_param)
@click.help_option('--help', '-h')
@environment.pass_env
def cli(env, name, region):
    """Create bandwidth pool.

    Region can be the full zone name 'SJC/DAL/WDC/TOR/MON', or just a single datacenter like 'SJC'.

    Example::
        slcli bandwidth pool-create --name testPool --region DAL
        slcli bandwidth pool-create --name testPool --region SJC/DAL/WDC/TOR/MON
    """

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
