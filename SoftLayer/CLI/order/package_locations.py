"""List packages."""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering

COLUMNS = ['id', 'dc', 'description', 'keyName']


@click.command()
@click.argument('package_keyname')
@environment.pass_env
def cli(env, package_keyname):
    """List Datacenters a package can be ordered in.

    Use the location Key Name to place orders
    """
    manager = ordering.OrderingManager(env.client)
    table = formatting.Table(COLUMNS)

    locations = manager.package_locations(package_keyname)
    for region in locations:
        for datacenter in region['locations']:
            table.add_row([
                datacenter['location']['id'],
                datacenter['location']['name'],
                region['description'],
                region['keyname']
            ])
    env.fout(table)
