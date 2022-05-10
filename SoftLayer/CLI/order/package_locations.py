"""List packages."""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import network
from SoftLayer.managers import ordering

COLUMNS = ['id', 'dc', 'description', 'keyName', 'Note']


@click.command(cls=SLCommand)
@click.argument('package_keyname')
@environment.pass_env
def cli(env, package_keyname):
    """List Datacenters a package can be ordered in.

    Use the location Key Name to place orders
    """
    manager = ordering.OrderingManager(env.client)
    network_manager = network.NetworkManager(env.client)

    pods = network_manager.get_closed_pods()
    table = formatting.Table(COLUMNS)

    locations = manager.package_locations(package_keyname)
    for region in locations:
        for datacenter in region['locations']:
            closure = []
            for pod in pods:
                if datacenter['location']['name'] in str(pod['name']):
                    closure.append(pod['name'])

            notes = '-'
            if len(closure) > 0:
                notes = 'closed soon: %s' % (', '.join(closure))
            table.add_row([
                datacenter['location']['id'],
                datacenter['location']['name'],
                region['description'],
                region['keyname'], notes
            ])
    env.fout(table)
