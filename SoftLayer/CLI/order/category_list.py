"""List package categories."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering

COLUMNS = ['name', 'categoryCode', 'isRequired']


@click.command()
@click.argument('package_keyname')
@click.option('--required',
              is_flag=True,
              help="List only the required categories for the package")
@environment.pass_env
def cli(env, package_keyname, required):
    """List the categories of a package.

    ::

        # List the categories of Bare Metal servers
        slcli order category-list BARE_METAL_SERVER

        # List the required categories for Bare Metal servers
        slcli order category-list BARE_METAL_SERVER --required

    """
    client = env.client
    manager = ordering.OrderingManager(client)
    table = formatting.Table(COLUMNS)

    categories = manager.list_categories(package_keyname)

    if required:
        categories = [cat for cat in categories if cat['isRequired']]

    for cat in categories:
        table.add_row([
            cat['itemCategory']['name'],
            cat['itemCategory']['categoryCode'],
            'Y' if cat['isRequired'] else 'N'
        ])

    env.fout(table)
