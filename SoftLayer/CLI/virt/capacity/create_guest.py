"""List Reserved Capacity"""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.CLI.virt.create import _parse_create_args as _parse_create_args
from SoftLayer.CLI.virt.create import _update_with_like_args as _update_with_like_args
from SoftLayer.managers.vs_capacity import CapacityManager as CapacityManager


@click.command()
@click.option('--capacity-id', type=click.INT, help="Reserve capacity Id to provision this guest into.")
@click.option('--primary-disk', type=click.Choice(['25', '100']), default='25', help="Size of the main drive.")
@click.option('--hostname', '-H', required=True, prompt=True, help="Host portion of the FQDN.")
@click.option('--domain', '-D', required=True, prompt=True, help="Domain portion of the FQDN.")
@click.option('--os', '-o', help="OS install code. Tip: you can specify <OS>_LATEST.")
@click.option('--image', help="Image ID. See: 'slcli image list' for reference.")
@click.option('--boot-mode', type=click.STRING,
              help="Specify the mode to boot the OS in. Supported modes are HVM and PV.")
@click.option('--postinstall', '-i', help="Post-install script to download.")
@helpers.multi_option('--key', '-k', help="SSH keys to add to the root user.")
@helpers.multi_option('--disk', help="Additional disk sizes.")
@click.option('--private', is_flag=True, help="Forces the VS to only have access the private network.")
@click.option('--like', is_eager=True, callback=_update_with_like_args,
              help="Use the configuration from an existing VS.")
@click.option('--network', '-n', help="Network port speed in Mbps.")
@helpers.multi_option('--tag', '-g', help="Tags to add to the instance.")
@click.option('--userdata', '-u', help="User defined metadata string.")
@click.option('--ipv6', is_flag=True, help="Adds an IPv6 address to this guest")
@click.option('--test', is_flag=True,
              help="Test order, will return the order container, but not actually order a server.")
@environment.pass_env
def cli(env, **args):
    """Allows for creating a virtual guest in a reserved capacity."""
    create_args = _parse_create_args(env.client, args)
    if args.get('ipv6'):
        create_args['ipv6'] = True
    create_args['primary_disk'] = args.get('primary_disk')
    manager = CapacityManager(env.client)
    capacity_id = args.get('capacity_id')
    test = args.get('test')

    result = manager.create_guest(capacity_id, test, create_args)

    env.fout(_build_receipt(result, test))


def _build_receipt(result, test=False):
    title = "OrderId: %s" % (result.get('orderId', 'No order placed'))
    table = formatting.Table(['Item Id', 'Description'], title=title)
    table.align['Description'] = 'l'

    if test:
        prices = result['prices']
    else:
        prices = result['orderDetails']['prices']

    for item in prices:
        table.add_row([item['id'], item['item']['description']])
    return table
