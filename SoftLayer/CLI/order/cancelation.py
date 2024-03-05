"""List all cancelation."""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering
from SoftLayer import utils


@click.command(cls=SLCommand)
@environment.pass_env
def cli(env):
    """List all account cancelations"""
    table = formatting.Table([
        'Case Number', 'Items', 'Created', 'Status', 'Requested by'])

    manager = ordering.OrderingManager(env.client)
    cancelations = manager.get_all_cancelation()

    for item in cancelations:
        table.add_row([item.get('ticketId'), item.get('itemCount'),
                       utils.clean_time(item.get('createDate'),
                                        in_format='%Y-%m-%dT%H:%M:%S', out_format='%Y-%m-%d %H:%M'),
                       item['status']['name'],
                       item['user']['firstName'] + ' ' + item['user']['lastName']
                       ])

    env.fout(table)
