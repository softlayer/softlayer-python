"""Order a IPSec VPN tunnel."""
# :licenses: MIT, see LICENSE for more details.

import click

import SoftLayer

from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.option('--datacenter', '-d', required=True, prompt=True, help="Datacenter shortname")
@environment.pass_env
def cli(env, datacenter):
    """Order/create a IPSec VPN tunnel instance."""

    ipsec_manager = SoftLayer.IPSECManager(env.client)

    if not (env.skip_confirmations or formatting.confirm(
            "This action will incur charges on your account. Continue?")):
        raise exceptions.CLIAbort('Aborting ipsec order.')

    result = ipsec_manager.order(datacenter, ['IPSEC_STANDARD'])

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['Id', result['orderId']])
    table.add_row(['Created', result['orderDate']])
    table.add_row(['Name', result['placedOrder']['items'][0]['description']])

    env.fout(table)
