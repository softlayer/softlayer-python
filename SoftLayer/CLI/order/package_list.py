"""List package presets."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering

COLUMNS = ['name',
           'keyName', ]


@click.command()
@click.option('--keyword',
              help="A word (or string) used to filter package names.")
@environment.pass_env
def cli(env, keyword):
    """List package presets."""
    manager = ordering.OrderingManager(env.client)
    table = formatting.Table(COLUMNS)

    _filter = {}
    if keyword:
        _filter = {'name': {'operation': '*= %s' % keyword}}

    packages = manager.list_packages(filter=_filter)

    for package in packages:
        table.add_row([
            package['name'],
            package['keyName'],
        ])
    env.fout(table)
