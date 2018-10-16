"""Shows the details of a reserved capacity group"""

import click

from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.vs_capacity import CapacityManager as CapacityManager

COLUMNS = [
    column_helper.Column('Id', ('id',)),
    column_helper.Column('hostname', ('hostname',)),
    column_helper.Column('domain', ('domain',)),
    column_helper.Column('primary_ip', ('primaryIpAddress',)),
    column_helper.Column('backend_ip', ('primaryBackendIpAddress',)),
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
    """Reserved Capacity Group details. Will show which guests are assigned to a reservation."""

    manager = CapacityManager(env.client)
    mask = """mask[instances[id,createDate,guestId,billingItem[id, description, recurringFee, category[name]],
              guest[modifyDate,id, primaryBackendIpAddress, primaryIpAddress,domain, hostname]]]"""
    result = manager.get_object(identifier, mask)

    try:
        flavor = result['instances'][0]['billingItem']['description']
    except KeyError:
        flavor = "Pending Approval..."

    table = formatting.Table(columns.columns, title="%s - %s" % (result.get('name'), flavor))
    # RCI = Reserved Capacity Instance
    for rci in result['instances']:
        guest = rci.get('guest', None)
        if guest is not None:
            table.add_row([value or formatting.blank() for value in columns.row(guest)])
        else:
            table.add_row(['-' for value in columns.columns])
    env.fout(table)
