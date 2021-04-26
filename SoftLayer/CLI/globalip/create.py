"""Creates a global IP."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command()
@click.option('-v6', '--ipv6', is_flag=True, help='Order a IPv6 IP')
@click.option('--test', help='test order')
@environment.pass_env
def cli(env, ipv6, test):
    """Creates a global IP."""

    mgr = SoftLayer.NetworkManager(env.client)

    version = 4
    if ipv6:
        version = 6

    if not (test or env.skip_confirmations):
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
    env.fout(table)
