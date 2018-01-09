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
    """List package presets.

    Package keynames can be retrieved from `slcli order package-list`.
    Some packages do not have presets.

    \b
    Example:
        # List the presets for Bare Metal servers
        slcli order preset-list BARE_METAL_SERVER

    The --keyword option can also be used for additional filtering on
    the returned presets.

    \b
    Example:
        # List the Bare Metal server presets that include a GPU
        slcli order preset-list BARE_METAL_SERVER --keyword gpu

    """
    table = formatting.Table(COLUMNS)
    manager = ordering.OrderingManager(env.client)

    _filter = {}
    if keyword:
        _filter = {'activePresets': {'name': {'operation': '*= %s' % keyword}}}
    presets = manager.list_presets(package_keyname, filter=_filter)

    for preset in presets:
        table.add_row([
            preset['name'],
            preset['keyName'],
            preset['description']
        ])
    env.fout(table)
