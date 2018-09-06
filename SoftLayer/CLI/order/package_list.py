"""List packages."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering

COLUMNS = ['id',
           'name',
           'keyName',
           'type']


@click.command()
@click.option('--keyword', help="A word (or string) used to filter package names.")
@click.option('--package_type', help="The keyname for the type of package. BARE_METAL_CPU for example")
@environment.pass_env
def cli(env, keyword, package_type):
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

    Package types can be used to remove unwanted packages
    \b
    Example:
        slcli order package-list --package_type BARE_METAL_CPU
    """
    manager = ordering.OrderingManager(env.client)
    table = formatting.Table(COLUMNS)

    _filter = {'type': {'keyName': {'operation': '!= BLUEMIX_SERVICE'}}}
    if keyword:
        _filter['name'] = {'operation': '*= %s' % keyword}
    if package_type:
        _filter['type'] = {'keyName': {'operation': package_type}}

    packages = manager.list_packages(filter=_filter)

    for package in packages:
        table.add_row([
            package['id'],
            package['name'],
            package['keyName'],
            package['type']['keyName']
        ])
    env.fout(table)
