"""Summary info about tickets."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """Summary info about tickets."""

    mask = ('openTicketCount, closedTicketCount, '
            'openBillingTicketCount, openOtherTicketCount, '
            'openSalesTicketCount, openSupportTicketCount, '
            'openAccountingTicketCount')
    account = env.client['Account'].getObject(mask=mask)
    table = formatting.Table(['Status', 'count'])

    nested = formatting.Table(['Type', 'count'])
    nested.add_row(['Accounting',
                    account['openAccountingTicketCount']])
    nested.add_row(['Billing', account['openBillingTicketCount']])
    nested.add_row(['Sales', account['openSalesTicketCount']])
    nested.add_row(['Support', account['openSupportTicketCount']])
    nested.add_row(['Other', account['openOtherTicketCount']])
    nested.add_row(['Total', account['openTicketCount']])
    table.add_row(['Open', nested])
    table.add_row(['Closed', account['closedTicketCount']])

    env.fout(table)
