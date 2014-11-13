"""Get details for an iSCSI target."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import formatting
from softlayer.cli import helpers
from softlayer import utils

import click


@click.command()
@click.argument('identifier')
@click.option('--password',
              is_flag=True,
              help="Show credentials to access the iSCSI target")
@environment.pass_env
def cli(env, identifier, password):
    """Get details for an iSCSI target."""

    iscsi_mgr = softlayer.ISCSIManager(env.client)

    iscsi_id = helpers.resolve_id(iscsi_mgr.resolve_ids, identifier, 'iSCSI')
    result = iscsi_mgr.get_iscsi(iscsi_id)
    result = utils.NestedDict(result)

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'

    table.add_row(['id', result['id']])
    table.add_row(['serviceResourceName', result['serviceResourceName']])
    table.add_row(['createDate', result['createDate']])
    table.add_row(['nasType', result['nasType']])
    table.add_row(['capacityGb', result['capacityGb']])

    if result['snapshotCapacityGb']:
        table.add_row(['snapshotCapacityGb', result['snapshotCapacityGb']])

    table.add_row(['mountableFlag', result['mountableFlag']])
    table.add_row(['serviceResourceBackendIpAddress',
                   result['serviceResourceBackendIpAddress']])
    table.add_row(['price', result['billingItem']['recurringFee']])
    table.add_row(['BillingItemId', result['billingItem']['id']])
    if result.get('notes'):
        table.add_row(['notes', result['notes']])

    if password:
        pass_table = formatting.Table(['username', 'password'])
        pass_table.add_row([result['username'], result['password']])
        table.add_row(['users', pass_table])

    return table
