"""Shows the details of a reserved capacity group"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.vs_capacity import CapacityManager as CapacityManager

COLUMNS = [
    column_helper.Column('guid', ('globalIdentifier',)),
    column_helper.Column('primary_ip', ('primaryIpAddress',)),
    column_helper.Column('backend_ip', ('primaryBackendIpAddress',)),
    column_helper.Column('datacenter', ('datacenter', 'name')),
    column_helper.Column('action', lambda guest: formatting.active_txn(guest),
                         mask='''
                         activeTransaction[
                            id,transactionStatus[name,friendlyName]
                         ]'''),
    column_helper.Column('power_state', ('powerState', 'name')),
    column_helper.Column(
        'created_by',
        ('billingItem', 'orderItem', 'order', 'userRecord', 'username')),
    column_helper.Column(
        'tags',
        lambda server: formatting.tags(server.get('tagReferences')),
        mask="tagReferences.tag.name"),
]

DEFAULT_COLUMNS = [
    'id',
    'hostname',
    'domain',
    'primary_ip',
    'backend_ip'
]

@click.command(epilog="Once provisioned, virtual guests can be managed with the slcli vs commands")
@click.argument('identifier')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. [options: %s]'
              % ', '.join(column.name for column in COLUMNS),
              default=','.join(DEFAULT_COLUMNS),
              show_default=True)
@environment.pass_env
def cli(env, identifier, columns):
    """Reserved Capacity Group Details"""
    manager = CapacityManager(env.client)
    mask = "mask[instances[billingItem[category], guest]]"
    result = manager.get_object(identifier, mask)
    try:
        flavor = result['instances'][0]['billingItem']['description']
    except KeyError:
        flavor = "Pending Approval..."

    table = formatting.Table(columns.columns, 
        title = "%s - %s" % (result.get('name'), flavor)
    )
    for rci in result['instances']:
        guest = rci.get('guest', None)
        guest_string = "---"
        createDate = rci['createDate']
        if guest is not None:
            guest_string = "%s (%s)" % (
                guest.get('fullyQualifiedDomainName', 'No FQDN'), 
                guest.get('primaryIpAddress', 'No Public Ip')
            )
            createDate = guest['modifyDate']
            table.add_row([value or formatting.blank() for value in columns.row(guest)])
        else:
            table.add_row(['-' for value in columns.columns])
    env.fout(table)


