"""Order/create a dedicated server."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.CLI import template


@click.command(epilog="See 'slcli server create-options' for valid options.")
@click.option('--hostname', '-H', required=True, prompt=True, help="Host portion of the FQDN")
@click.option('--domain', '-D', required=True, prompt=True, help="Domain portion of the FQDN")
@click.option('--size', '-s', required=True, prompt=True, help="Hardware size")
@click.option('--os', '-o', required=True, prompt=True, help="OS Key value")
@click.option('--datacenter', '-d', required=True, prompt=True, help="Datacenter shortname")
@click.option('--port-speed', type=click.INT, help="Port speeds. DEPRECATED, use --network")
@click.option('--no-public', is_flag=True, help="Private network only. DEPRECATED, use --network.")
@click.option('--network', help="Network Option Key. Use instead of port-speed option")
@click.option('--billing', default='hourly', show_default=True, type=click.Choice(['hourly', 'monthly']),
              help="Billing rate")
@click.option('--postinstall', '-i', help="Post-install script. Should be a HTTPS URL.")
@click.option('--test', is_flag=True, help="Do not actually create the server")
@click.option('--template', '-t', is_eager=True, type=click.Path(exists=True, readable=True, resolve_path=True),
              callback=template.TemplateCallback(list_args=['key']),
              help="A template file that defaults the command-line options")
@click.option('--export', type=click.Path(writable=True, resolve_path=True),
              help="Exports options to a template file")
@click.option('--wait', type=click.INT,
              help="Wait until the server is finished provisioning for up to X seconds before returning")
@click.option('--router-public', type=click.INT,
              help="The ID of the public ROUTER on which you want the virtual server placed")
@click.option('--router-private', type=click.INT,
              help="The ID of the private ROUTER on which you want the virtual server placed")
@helpers.multi_option('--key', '-k', help="SSH keys to add to the root user")
@helpers.multi_option('--extra', '-e', help="Extra option Key Names")
@environment.pass_env
def cli(env, **args):
    """Order/create a dedicated server."""
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
        'location': args.get('datacenter'),
        'ssh_keys': ssh_keys,
        'post_uri': args.get('postinstall'),
        'os': args['os'],
        'hourly': args.get('billing') == 'hourly',
        'port_speed': args.get('port_speed'),
        'no_public': args.get('no_public') or False,
        'extras': args.get('extra'),
        'network': args.get('network'),
        'public_router': args.get('router_public', None),
        'private_router': args.get('router_private', None)
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
        template.export_to_template(export_file, args, exclude=['wait', 'test'])
        env.fout('Successfully exported options to a template file.')
        return

    if do_create:
        if not (env.skip_confirmations or formatting.confirm(
                "This action will incur charges on your account. Continue?")):
            raise exceptions.CLIAbort('Aborting dedicated server order.')

        result = mgr.place_order(**order)

        table = formatting.KeyValueTable(['name', 'value'])
        table.align['name'] = 'r'
        table.align['value'] = 'l'
        table.add_row(['id', result['orderId']])
        table.add_row(['created', result['orderDate']])
        output = table

    env.fout(output)
