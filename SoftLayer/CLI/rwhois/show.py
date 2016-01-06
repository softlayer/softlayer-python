"""Display the RWhois information for your account."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """Display the RWhois information for your account."""

    mgr = SoftLayer.NetworkManager(env.client)
    result = mgr.get_rwhois()

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['Name', result['firstName'] + ' ' + result['lastName']])
    table.add_row(['Company', result['companyName']])
    table.add_row(['Abuse Email', result['abuseEmail']])
    table.add_row(['Address 1', result['address1']])
    if result.get('address2'):
        table.add_row(['Address 2', result['address2']])
    table.add_row(['City', result['city']])
    table.add_row(['State', result.get('state', '-')])
    table.add_row(['Postal Code', result.get('postalCode', '-')])
    table.add_row(['Country', result['country']])
    table.add_row(['Private Residence', result['privateResidenceFlag']])

    env.fout(table)
