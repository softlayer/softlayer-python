"""Save a quote"""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering
from SoftLayer.utils import clean_time


@click.command()
@click.argument('quote')
@environment.pass_env
def cli(env, quote):
    """Save a quote"""

    manager = ordering.OrderingManager(env.client)
    result = manager.save_quote(quote)

    table = formatting.Table([
        'Id', 'Name', 'Created', 'Modified', 'Status'
    ])
    table.align['Name'] = 'l'

    table.add_row([
        result.get('id'),
        result.get('name'),
        clean_time(result.get('createDate')),
        clean_time(result.get('modifyDate')),
        result.get('status'),
    ])

    env.fout(table)
