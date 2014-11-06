"""Order/create a dedicated server."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.CLI import server
from SoftLayer.CLI import template

import click


@click.command(epilog="""See 'sl server list-chassis' and
 'sl server create-options' for valid options.""")
@click.option('--domain', '-D',
              help="Domain portion of the FQDN")
@click.option('--hostname', '-H',
              help="Host portion of the FQDN")
@click.option('--chassis',
              help="The chassis to use for the new server")
@click.option('--cpu', '-c',
              help="Number of CPU cores",
              type=click.INT)
@click.option('--memory', '-m',
              help="Memory in mebibytes",
              type=click.INT)
@click.option('--os', '-o',
              help="OS install code. Tip: you can specify <OS>_LATEST")
@click.option('--billing',
              type=click.Choice(['hourly', 'monthly']),
              default='monthly',
              help="""Billing rate.
The hourly rate is only available on bare metal instances""")
@click.option('--datacenter', '-d', help="Datacenter shortname")
@click.option('--dedicated/--public',
              is_flag=True,
              help="Create a dedicated Virtual Server (Private Node)")
@click.option('--san',
              is_flag=True,
              help="Use SAN storage instead of local disk.")
@click.option('--test',
              is_flag=True,
              help="Do not actually create the virtual server")
@click.option('--export',
              type=click.Path(writable=True, resolve_path=True),
              help="Exports options to a template file")
@click.option('--userfile', '-F',
              help="Read userdata from file",
              type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--postinstall', '-i', help="Post-install script to download")
@helpers.multi_option('--key', '-k',
                      help="SSH keys to add to the root user")
@helpers.multi_option('--disk', help="Disk sizes")
@click.option('--controller', help="The RAID configuration for the server")
@click.option('--private',
              is_flag=True,
              help="Forces the VS to only have access the private network")
@click.option('--network', '-n', help="Network port speed in Mbps")
@click.option('--template', '-t',
              help="A template file that defaults the command-line options",
              type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--userdata', '-u', help="User defined metadata string")
@click.option('--vlan-public',
              help="The ID of the public VLAN on which you want the virtual "
              "server placed",
              type=click.INT)
@click.option('--vlan-private',
              help="The ID of the private VLAN on which you want the virtual "
                   "server placed",
              type=click.INT)
@click.option('--wait',
              type=click.INT,
              help="Wait until the server is finished provisioning for up to "
                   "X seconds before returning")
@environment.pass_env
def cli(env, **args):
    """Order/create a dedicated server."""

    template.update_with_template_args(args, list_args=['disk', 'key'])
    mgr = SoftLayer.HardwareManager(env.client)

    ds_options = mgr.get_dedicated_server_create_options(args['chassis'])

    order = _process_args(env, args, ds_options)

    # Do not create hardware server with --test or --export
    do_create = not (args['export'] or args['test'])

    output = None
    if args.get('test'):
        result = mgr.verify_order(**order)

        table = formatting.Table(['Item', 'cost'])
        table.align['Item'] = 'r'
        table.align['cost'] = 'r'

        total = 0.0
        for price in result['prices']:
            total += float(price.get('recurringFee', 0.0))
            rate = "%.2f" % float(price['recurringFee'])

            table.add_row([price['item']['description'], rate])

        table.add_row(['Total monthly cost', "%.2f" % total])
        output = []
        output.append(table)
        output.append(formatting.FormattedItem(
            '',
            ' -- ! Prices reflected here are retail and do not '
            'take account level discounts and are not guaranteed.'))

    if args['export']:
        export_file = args.pop('export')
        template.export_to_template(export_file, args,
                                    exclude=['wait', 'test'])
        return 'Successfully exported options to a template file.'

    if do_create:
        if env.skip_confirmations or formatting.confirm(
                "This action will incur charges on your account. "
                "Continue?"):
            result = mgr.place_order(**order)

            table = formatting.KeyValueTable(['name', 'value'])
            table.align['name'] = 'r'
            table.align['value'] = 'l'
            table.add_row(['id', result['orderId']])
            table.add_row(['created', result['orderDate']])
            output = table
        else:
            raise exceptions.CLIAbort('Aborting dedicated server order.')

    return output


def _process_args(env, args, ds_options):
    """Convert CLI arguments to VSManager.create_hardware arguments."""
    mgr = SoftLayer.HardwareManager(env.client)

    order = {
        'hostname': args['hostname'],
        'domain': args['domain'],
        'bare_metal': False,
        'package_id': args['chassis'],
    }

    # Determine if this is a "Bare Metal Instance" or regular server
    bmc = False
    if args['chassis'] == str(mgr.get_bare_metal_package_id()):
        bmc = True

    # Convert the OS code back into a price ID
    os_price = _get_price_id_from_options(ds_options, 'os', args['os'])

    if os_price:
        order['os'] = os_price
    else:
        raise exceptions.CLIAbort('Invalid operating system specified.')

    order['location'] = args['datacenter']

    if bmc:
        order['server'] = _get_cpu_and_memory_price_ids(ds_options,
                                                        args['cpu'],
                                                        args['memory'])
        order['bare_metal'] = True

        if args['billing'] == 'hourly':
            order['hourly'] = True
    else:
        order['server'] = args['cpu']
        order['ram'] = _get_price_id_from_options(
            ds_options, 'memory', int(args['memory']))

    # Set the disk sizes
    disk_prices = []
    disk_number = 0
    for disk in args.get('disk'):
        disk_price = _get_disk_price(ds_options, disk, disk_number)
        disk_number += 1
        if disk_price:
            disk_prices.append(disk_price)

    if not disk_prices:
        disk_prices.append(_get_default_value(ds_options, 'disk0'))

    order['disks'] = disk_prices

    # Set the disk controller price
    if not bmc:
        if args.get('controller'):
            dc_price = _get_price_id_from_options(ds_options,
                                                  'disk_controller',
                                                  args.get('controller'))
        else:
            dc_price = _get_price_id_from_options(ds_options,
                                                  'disk_controller',
                                                  'None')

        order['disk_controller'] = dc_price

    # Set the port speed
    port_speed = args.get('network')

    nic_price = _get_price_id_from_options(ds_options, 'nic', port_speed)

    if nic_price:
        order['port_speed'] = nic_price
    else:
        raise exceptions.CLIAbort('Invalid NIC speed specified.')

    if args.get('postinstall'):
        order['post_uri'] = args.get('postinstall')

    # Get the SSH keys
    if args.get('key'):
        keys = []
        for key in args.get('key'):
            resolver = SoftLayer.SshKeyManager(env.client).resolve_ids
            key_id = helpers.resolve_id(resolver, key, 'SshKey')
            keys.append(key_id)
        order['ssh_keys'] = keys

    if args.get('vlan_public'):
        order['public_vlan'] = args['vlan_public']

    if args.get('vlan_private'):
        order['private_vlan'] = args['vlan_private']

    return order


def _get_default_value(ds_options, option):
    """Returns a 'free' price id given an option."""
    if option not in ds_options['categories']:
        return

    for item in ds_options['categories'][option]['items']:
        if not any([
                float(item.get('setupFee', 0)),
                float(item.get('recurringFee', 0)),
                float(item.get('hourlyRecurringFee', 0)),
                float(item.get('oneTimeFee', 0)),
                float(item.get('laborFee', 0)),
        ]):
            return item['price_id']


def _get_disk_price(ds_options, value, number):
    """Returns a price id that matches a given disk config."""
    if not number:
        return _get_price_id_from_options(ds_options, 'disk', value)
    # This will get the item ID for the matching identifier string, which
    # we can then use to get the price ID for our specific disk
    item_id = _get_price_id_from_options(ds_options, 'disk', value, True)
    key = 'disk' + str(number)
    if key in ds_options['categories']:
        for item in ds_options['categories'][key]['items']:
            if item['id'] == item_id:
                return item['price_id']


def _get_cpu_and_memory_price_ids(ds_options, cpu_value, memory_value):
    """Returns a price id for a cpu/memory pair in pre-configured servers.

    (formerly known as BMC).
    """
    for memory, options in server.get_create_options(ds_options,
                                                     'server_core',
                                                     False):
        if int(memory) == int(memory_value):
            for cpu_size, price_id in options:
                if int(cpu_size) == int(cpu_value):
                    return price_id

    raise exceptions.CLIAbort('No price found for CPU/Memory combination')


def _get_price_id_from_options(ds_options, option, value, item_id=False):
    """Returns a price_id for a given option and value."""

    for _, options in server.get_create_options(ds_options, option, False):
        for item_options in options:
            if item_options[0] == value:
                if not item_id:
                    return item_options[1]
                return item_options[2]
    raise exceptions.CLIAbort('No price found for %s' % option)
