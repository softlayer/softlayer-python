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

    .. Note::
        Presets are set CPU / RAM / Disk allotments. You still need to specify required items.
        Some packages do not have presets.

    ::

        # List the presets for Bare Metal servers
        slcli order preset-list BARE_METAL_SERVER

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
            str(preset['name']).strip(),
            str(preset['keyName']).strip(),
            str(preset['description']).strip()
        ])
    env.fout(table)
