"""Order/create a dedicated server."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.CLI import template

import click


@click.command(epilog="See 'slcli server create-options' for valid options.")
@click.option('--hostname', '-H', help="Host portion of the FQDN")
@click.option('--domain', '-D', help="Domain portion of the FQDN")
@click.option('--size', '-s', help="Hardware size")
@click.option('--os', '-o', help="OS install code")
@click.option('--datacenter', '-d', help="Datacenter shortname")
@click.option('--port-speed', type=click.INT, help="Port speeds")
@click.option('--billing',
              type=click.Choice(['hourly', 'monthly']),
              default='hourly',
              help="Billing rate")
@click.option('--postinstall', '-i', help="Post-install script to download")
@helpers.multi_option('--key', '-k',
                      help="SSH keys to add to the root user")
@click.option('--vlan-public',
              help="The ID of the public VLAN on which you want the virtual "
              "server placed",
              type=click.INT)
@click.option('--vlan-private',
              help="The ID of the private VLAN on which you want the virtual "
                   "server placed",
              type=click.INT)
@helpers.multi_option('--extra', '-e', help="Extra options")
@click.option('--test',
              is_flag=True,
              help="Do not actually create the virtual server")
@click.option('--template', '-t',
              help="A template file that defaults the command-line options",
              type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--export',
              type=click.Path(writable=True, resolve_path=True),
              help="Exports options to a template file")
@click.option('--wait',
              type=click.INT,
              help="Wait until the server is finished provisioning for up to "
                   "X seconds before returning")
@environment.pass_env
def cli(env, **args):
    """Order/create a dedicated server."""

    template.update_with_template_args(args, list_args=['key'])
    _validate_args(args)

    mgr = SoftLayer.HardwareManager(env.client)

    # Get the SSH keys
    ssh_keys = []
    for key in args.get('key'):
        resolver = SoftLayer.SshKeyManager(env.client).resolve_ids
        key_id = helpers.resolve_id(resolver, key, 'SshKey')
        ssh_keys.append(key_id)

    order = {
        'hostname': args['hostname'],
        'domain': args['domain'],
        'size': args['size'],
        'public_vlan': args.get('vlan_public'),
        'private_vlan': args.get('vlan_private'),
        'location': args.get('datacenter'),
        'ssh_keys': ssh_keys,
        'post_uri': args.get('postinstall'),
        'os': args['os'],
        'hourly': args.get('billing') == 'hourly',
        'port_speed': args.get('port_speed'),
        'no_public': args.get('no_public') or False,
        'extras': args.get('extra'),
    }

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
        if not (env.skip_confirmations or formatting.confirm(
                "This action will incur charges on your account. "
                "Continue?")):
            raise exceptions.CLIAbort('Aborting dedicated server order.')

        result = mgr.place_order(**order)

        table = formatting.KeyValueTable(['name', 'value'])
        table.align['name'] = 'r'
        table.align['value'] = 'l'
        table.add_row(['id', result['orderId']])
        table.add_row(['created', result['orderDate']])
        output = table

    return output


def _validate_args(args):
    """Raises an ArgumentError if the given arguments are not valid."""
    missing = []
    for arg in ['size',
                'datacenter',
                'os',
                'port_speed',
                'hostname',
                'domain']:
        if not args.get(arg):
            missing.append(arg)

    if missing:
        raise exceptions.ArgumentError('Missing required options: %s'
                                       % ', '.join(missing))
