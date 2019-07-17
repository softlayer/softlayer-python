"""Account Summary page"""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import utils


@click.command()
@environment.pass_env
def cli(env):
    """Prints some various bits of information about an account"""

    manager = AccountManager(env.client)
    summary = manager.get_summary()
    env.fout(get_snapshot_table(summary))


def get_snapshot_table(account):
    """Generates a table for printing account summary data"""
    table = formatting.KeyValueTable(["Name", "Value"], title="Account Snapshot")
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'
    table.add_row(['Company Name', account.get('companyName', '-')])
    table.add_row(['Balance', utils.lookup(account, 'pendingInvoice', 'startingBalance')])
    table.add_row(['Upcoming Invoice', utils.lookup(account, 'pendingInvoice', 'invoiceTotalAmount')])
    table.add_row(['Image Templates', account.get('blockDeviceTemplateGroupCount', '-')])
    table.add_row(['Dedicated Hosts', account.get('dedicatedHostCount', '-')])
    table.add_row(['Hardware', account.get('hardwareCount', '-')])
    table.add_row(['Virtual Guests', account.get('virtualGuestCount', '-')])
    table.add_row(['Domains', account.get('domainCount', '-')])
    table.add_row(['Network Storage Volumes', account.get('networkStorageCount', '-')])
    table.add_row(['Open Tickets', account.get('openTicketCount', '-')])
    table.add_row(['Network Vlans', account.get('networkVlanCount', '-')])
    table.add_row(['Subnets', account.get('subnetCount', '-')])
    table.add_row(['Users', account.get('userCount', '-')])
    return table
