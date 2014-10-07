"""Creates a global IP"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting

import click


@click.command()
@click.argument('identifier')
@click.option('--v6', is_flag=True, help='Order a IPv6 IP')
@click.option('--test', help='test order')
@environment.pass_env
def cli(env, identifier, v6, test):
    """Creates a global IP"""

    mgr = SoftLayer.NetworkManager(env.client)

    version = 4
    if v6:
        version = 6
    if not test and not env.skip_confirmations:
        if not formatting.confirm("This action will incur charges on your "
                                  "account. Continue?"):
            raise exceptions.CLIAbort('Cancelling order.')
    result = mgr.add_global_ip(version=version, test_order=test)

    table = formatting.Table(['item', 'cost'])
    table.align['Item'] = 'r'
    table.align['cost'] = 'r'

    total = 0.0
    for price in result['orderDetails']['prices']:
        total += float(price.get('recurringFee', 0.0))
        rate = "%.2f" % float(price['recurringFee'])

        table.add_row([price['item']['description'], rate])

    table.add_row(['Total monthly cost', "%.2f" % total])
    return table
