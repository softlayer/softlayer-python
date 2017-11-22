"""List package presets."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering

COLUMNS = ['name',
           'keyName',
           'description', ]


@click.command()
@click.argument('package_keyname')
@click.option('--keyword',
              help="A word (or string) used to filter preset names.")
@environment.pass_env
def cli(env, package_keyname, keyword):
    """List package presets."""
    table = formatting.Table(COLUMNS)
    manager = ordering.OrderingManager(env.client)

    _filter = {}
    if keyword:
        _filter = {'presets': {'name': {'operation': '*= %s' % keyword}}}
    presets = manager.list_presets(package_keyname, filter=_filter)

    for preset in presets:
        table.add_row([
            preset['name'],
            preset['keyName'],
            preset['description']
        ])
    env.fout(table)
