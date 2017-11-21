"""Order/create a dedicated Host."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command(
    epilog="See 'slcli dedicatedhost create-options' for valid options.")
@click.option('--hostname', '-H',
              help="Host portion of the FQDN",
              required=True,
              prompt=True)
@click.option('--router', '-r',
              help="Router id",
              show_default=True)
@click.option('--domain', '-D',
              help="Domain portion of the FQDN",
              required=True,
              prompt=True)
@click.option('--datacenter', '-d', help="Datacenter shortname",
              required=True,
              prompt=True)
@click.option('--billing',
              type=click.Choice(['hourly', 'monthly']),
              default='hourly',
              show_default=True,
              help="Billing rate")
@click.option('--test',
              is_flag=True,
              help="Do not actually create the server")
@helpers.multi_option('--extra', '-e', help="Extra options")
@environment.pass_env
def cli(env, **args):
    """Order/create a dedicated host."""
    mgr = SoftLayer.DedicatedHostManager(env.client)

    order = {
        'hostname': args['hostname'],
        'domain': args['domain'],
        'router': args['router'],
        'location': args.get('datacenter'),
        'hourly': args.get('billing') == 'hourly',
    }

    do_create = not (args['test'])

    output = None

    if args.get('test'):
        result = mgr.verify_order(**order)

        table = formatting.Table(['Item', 'cost'])
        table.align['Item'] = 'r'
        table.align['cost'] = 'r'

        for price in result['prices']:
            if order['hourly']:
                total = float(price.get('hourlyRecurringFee', 0.0))
                rate = "%.2f" % float(price['hourlyRecurringFee'])
            else:
                total = float(price.get('recurringFee', 0.0))
                rate = "%.2f" % float(price['recurringFee'])

        table.add_row([price['item']['description'], rate])

        if order['hourly']:
            table.add_row(['Total hourly cost', "%.2f" % total])
        else:
            table.add_row(['Total monthly cost', "%.2f" % total])

        output = []
        output.append(table)
        output.append(formatting.FormattedItem(
            '',
            ' -- ! Prices reflected here are retail and do not '
            'take account level discounts and are not guaranteed.'))

    if do_create:
        if not (env.skip_confirmations or formatting.confirm(
                "This action will incur charges on your account. "
                "Continue?")):
            raise exceptions.CLIAbort('Aborting dedicated host order.')

        result = mgr.place_order(**order)

        table = formatting.KeyValueTable(['name', 'value'])
        table.align['name'] = 'r'
        table.align['value'] = 'l'
        table.add_row(['id', result['orderId']])
        table.add_row(['created', result['orderDate']])
        output = table

    env.fout(output)
