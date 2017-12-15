"""Order/create a dedicated Host."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import template


@click.command(
    epilog="See 'slcli dedicatedhost create-options' for valid options.")
@click.option('--hostname', '-H',
              help="Host portion of the FQDN",
              required=True,
              prompt=True)
@click.option('--router', '-r',
              help="Router hostname ex. fcr02a.dal13",
              show_default=True)
@click.option('--domain', '-D',
              help="Domain portion of the FQDN",
              required=True,
              prompt=True)
@click.option('--datacenter', '-d', help="Datacenter shortname",
              required=True,
              prompt=True)
@click.option('--flavor', '-f', help="Dedicated Virtual Host flavor",
              required=True,
              prompt=True)
@click.option('--billing',
              type=click.Choice(['hourly', 'monthly']),
              default='hourly',
              show_default=True,
              help="Billing rate")
@click.option('--verify',
              is_flag=True,
              help="Verify dedicatedhost without creating it.")
@click.option('--template', '-t',
              is_eager=True,
              callback=template.TemplateCallback(list_args=['key']),
              help="A template file that defaults the command-line options",
              type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--export',
              type=click.Path(writable=True, resolve_path=True),
              help="Exports options to a template file")
@environment.pass_env
def cli(env, **kwargs):
    """Order/create a dedicated host."""
    mgr = SoftLayer.DedicatedHostManager(env.client)

    order = {
        'hostname': kwargs['hostname'],
        'domain': kwargs['domain'],
        'flavor': kwargs['flavor'],
        'location': kwargs['datacenter'],
        'hourly': kwargs.get('billing') == 'hourly',
    }

    if kwargs['router']:
        order['router'] = kwargs['router']

    do_create = not (kwargs['export'] or kwargs['verify'])

    output = None

    result = mgr.verify_order(**order)
    table = formatting.Table(['Item', 'cost'])
    table.align['Item'] = 'r'
    table.align['cost'] = 'r'
    if len(result['prices']) != 1:
        raise exceptions.ArgumentError("More than 1 price was found or no "
                                       "prices found")
    price = result['prices']
    if order['hourly']:
        total = float(price[0].get('hourlyRecurringFee', 0.0))
    else:
        total = float(price[0].get('recurringFee', 0.0))

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

    if kwargs['export']:
        export_file = kwargs.pop('export')
        template.export_to_template(export_file, kwargs,
                                    exclude=['wait', 'verify'])
        env.fout('Successfully exported options to a template file.')

    if do_create:
        if not env.skip_confirmations and not formatting.confirm(
                "This action will incur charges on your account. "
                "Continue?"):
            raise exceptions.CLIAbort('Aborting dedicated host order.')

        result = mgr.place_order(**order)

        table = formatting.KeyValueTable(['name', 'value'])
        table.align['name'] = 'r'
        table.align['value'] = 'l'
        table.add_row(['id', result['orderId']])
        table.add_row(['created', result['orderDate']])
        output.append(table)

    env.fout(output)
