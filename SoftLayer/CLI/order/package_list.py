"""List packages."""
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
    """List packages that can be ordered via the placeOrder API.

    \b
    Example:
        # List out all packages for ordering
        slcli order package-list


    Keywords can also be used for some simple filtering functionality
    to help find a package easier.

    \b
    Example:
        # List out all packages with "server" in the name
        slcli order package-list --keyword server

    """
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
