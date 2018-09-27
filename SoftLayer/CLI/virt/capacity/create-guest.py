"""List Reserved Capacity"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.CLI.virt.create import _update_with_like_args as _update_with_like_args
from SoftLayer.managers.vs_capacity import CapacityManager as CapacityManager


from pprint import pprint as pp



def _parse_create_args(client, args):
    """Parses CLI arguments into a single data structure to be used by vs_capacity::create_guest.

    :param dict args: CLI arguments
    """
    data = {
        "hourly": True,
        "domain": args['domain'],
        "hostname": args['hostname'],
        "private": args['private'],
        "disks": args['disk'],
        "boot_mode": args.get('boot_mode', None),
        "local_disk": None
    }
    if args.get('os'):
        data['os_code'] = args['os']

    if args.get('image'):
        if args.get('image').isdigit():
            image_mgr = SoftLayer.ImageManager(client)
            image_details = image_mgr.get_image(args.get('image'),
                                                mask="id,globalIdentifier")
            data['image_id'] = image_details['globalIdentifier']
        else:
            data['image_id'] = args['image']

    if args.get('network'):
        data['nic_speed'] = args.get('network')

    if args.get('userdata'):
        data['userdata'] = args['userdata']
    elif args.get('userfile'):
        with open(args['userfile'], 'r') as userfile:
            data['userdata'] = userfile.read()

    if args.get('postinstall'):
        data['post_uri'] = args.get('postinstall')

    # Get the SSH keys
    if args.get('key'):
        keys = []
        for key in args.get('key'):
            resolver = SoftLayer.SshKeyManager(client).resolve_ids
            key_id = helpers.resolve_id(resolver, key, 'SshKey')
            keys.append(key_id)
        data['ssh_keys'] = keys

    if args.get('vlan_public'):
        data['public_vlan'] = args['vlan_public']

    if args.get('vlan_private'):
        data['private_vlan'] = args['vlan_private']

    data['public_subnet'] = args.get('subnet_public', None)

    data['private_subnet'] = args.get('subnet_private', None)

    if args.get('public_security_group'):
        pub_groups = args.get('public_security_group')
        data['public_security_groups'] = [group for group in pub_groups]

    if args.get('private_security_group'):
        priv_groups = args.get('private_security_group')
        data['private_security_groups'] = [group for group in priv_groups]

    if args.get('tag'):
        data['tags'] = ','.join(args['tag'])

    if args.get('host_id'):
        data['host_id'] = args['host_id']

    if args.get('ipv6'):
        data['ipv6'] = True

    data['primary_disk'] = args.get('primary_disk')

    return data


@click.command()
@click.option('--capacity-id', type=click.INT, help="Reserve capacity Id to provision this guest into.")
@click.option('--primary-disk', type=click.Choice(['25','100']), default='25', help="Size of the main drive." )
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
    create_args = _parse_create_args(env.client, args)
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

