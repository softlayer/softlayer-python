"""List Users."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

TWO_FACTO_AUTH = 'externalBindingCount'
CLASSIC_API_KEYS = 'apiAuthenticationKeyCount'

COLUMNS = [
    column_helper.Column('id', ('id',)),
    column_helper.Column('username', ('username',)),
    column_helper.Column('email', ('email',)),
    column_helper.Column('displayName', ('displayName',)),
    column_helper.Column('status', ('userStatus', 'name')),
    column_helper.Column('hardwareCount', ('hardwareCount',)),
    column_helper.Column('virtualGuestCount', ('virtualGuestCount',)),
    column_helper.Column('2FA', (TWO_FACTO_AUTH,)),
    column_helper.Column('classicAPIKey', (CLASSIC_API_KEYS,))
]

DEFAULT_COLUMNS = [
    'id',
    'username',
    'email',
    'displayName',
    '2FA',
    'classicAPIKey',
]


@click.command()
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. [options: %s]' % ', '.join(column.name for column in COLUMNS),
              default=','.join(DEFAULT_COLUMNS),
              show_default=True)
@environment.pass_env
def cli(env, columns):
    """List Users."""

    mgr = SoftLayer.UserManager(env.client)
    users = mgr.list_users()

    table = formatting.Table(columns.columns)
    for user in users:
        user = _yes_format(user, [TWO_FACTO_AUTH, CLASSIC_API_KEYS])
        table.add_row([value or formatting.blank()
                       for value in columns.row(user)])

    env.fout(table)


def _yes_format(user, keys):
    """Changes all dictionary values to yes whose keys are in the list. """
    for key in keys:
        if user.get(key):
            user[key] = 'yes'
    return user
