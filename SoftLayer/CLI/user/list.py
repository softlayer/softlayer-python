"""List Users."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers

from pprint import pprint as pp

COLUMNS = [
    column_helper.Column('id', ('id',)),
    column_helper.Column('username', ('username',)),
    column_helper.Column('displayName', ('displayName',)),
    column_helper.Column('status', ('userStatus', 'name')),
    column_helper.Column('hardwareCount', ('hardwareCount',)),
    column_helper.Column('virtualGuestCount', ('virtualGuestCount',)),
]

DEFAULT_COLUMNS = [
    'id',
    'username',
    'displayName',
    'status',
    'hardwareCount',
    'virtualGuestCount'
]
@click.command()
@click.option('--name', default=None, help='Filter on username')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. [options: %s]' % ', '.join(column.name for column in COLUMNS),
              default=','.join(DEFAULT_COLUMNS),
              show_default=True)
@environment.pass_env
def cli(env, name, columns):
    """List Users."""

    mgr = SoftLayer.UserManager(env.client)
    users = mgr.list_users()

    table = formatting.Table(columns.columns)
    for user in users:
        table.add_row([value or formatting.blank()
                       for value in columns.row(user)])

    env.fout(table)

