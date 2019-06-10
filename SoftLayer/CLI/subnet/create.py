"""Add a new subnet to your account."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(short_help="Add a new subnet to your account")
@click.argument('network', type=click.Choice(['static', 'public', 'private']))
@click.argument('quantity', type=click.INT)
@click.argument('endpoint-id', type=click.INT)
@click.option('--ipv6', '--v6', is_flag=True, help="Order IPv6 Addresses")
@click.option('--test',
              is_flag=True,
              help="Do not order the subnet; just get a quote")
@environment.pass_env
def cli(env, network, quantity, endpoint_id, ipv6, test):
    """Add a new subnet to your account. Valid quantities vary by type.

    \b
    IPv4
    static  - 1, 2, 4, 8, 16, 32, 64, 128, 256
    public  - 4, 8, 16, 32, 64, 128, 256
    private - 4, 8, 16, 32, 64, 128, 256

    \b
    IPv6
    static  - 64
    public  - 64

    \b
    endpoint-id
    static  - Network_Subnet_IpAddress identifier.
    public  - Network_Vlan identifier
    private - Network_Vlan identifier
"""

    mgr = SoftLayer.NetworkManager(env.client)

    if not (test or env.skip_confirmations):
        if not formatting.confirm("This action will incur charges on your "
                                  "account. Continue?"):
            raise exceptions.CLIAbort('Cancelling order.')

    version = 4
    if ipv6:
        version = 6

    try:
        result = mgr.add_subnet(network, quantity=quantity, endpoint_id=endpoint_id, version=version, test_order=test)

    except SoftLayer.SoftLayerAPIError as error:
        raise exceptions.CLIAbort('Unable to order {} {} ipv{} , error: {}'.format(quantity,
                                                                                   network,
                                                                                   version,
                                                                                   error.faultString))

    table = formatting.Table(['Item', 'cost'])
    table.align['Item'] = 'r'
    table.align['cost'] = 'r'

    total = 0.0
    if 'prices' in result:
        for price in result['prices']:
            total += float(price.get('recurringFee', 0.0))
            rate = "%.2f" % float(price['recurringFee'])

            table.add_row([price['item']['description'], rate])

    table.add_row(['Total monthly cost', "%.2f" % total])
    env.fout(table)
