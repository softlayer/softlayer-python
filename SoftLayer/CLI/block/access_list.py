"""List hosts with access to volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


def _format_name(obj):
    if obj['type'] == 'VIRTUAL':
        return "{0}.{1}".format(obj['hostname'], obj['domain'])

    elif obj['type'] == 'HARDWARE':
        return "{0}.{1}".format(obj['hostname'], obj['domain'])

    elif obj['type'] == 'SUBNET':
        name = "{0}/{1}".format(
            obj['networkIdentifier'],
            obj['cidr']
        )
        if 'note' in obj.keys():
            name = "{0} ({1})".format(name, obj['note'])

        return name

    elif obj['type'] == 'IP':
        name = obj['ipAddress']
        if 'note' in obj.keys():
            name = "{0} ({1})".format(name, obj['note'])

        return name
    else:
        raise Exception('Unknown type %s' % obj['type'])


COLUMNS = [
    column_helper.Column('id', ('id',)),
    column_helper.Column('name', _format_name, """
allowedVirtualGuests[hostname,domain],
allowedHardware[hostname,domain],
allowedSubnets[networkIdentifier,cidr,note],
allowedIpAddresses[ipAddress,note],
"""),
    column_helper.Column('type', ('type',)),
    column_helper.Column(
        'private_ip_address',
        ('primaryBackendIpAddress',),
        """
allowedVirtualGuests.primaryBackendIpAddress
allowedHardware.primaryBackendIpAddress
allowedSubnets.primaryBackendIpAddress
allowedIpAddresses.primaryBackendIpAddress
"""),
    column_helper.Column(
        'host_iqn',
        ('allowedHost', 'name',),
        """
allowedVirtualGuests.allowedHost.name
allowedHardware.allowedHost.name
allowedSubnets.allowedHost.name
allowedIpAddresses.allowedHost.name
"""),
    column_helper.Column(
        'username',
        ('allowedHost', 'credential', 'username',),
        """
allowedVirtualGuests.allowedHost.credential.username
allowedHardware.allowedHost.credential.username
allowedSubnets.allowedHost.credential.username
allowedIpAddresses.allowedHost.credential.username
"""),
    column_helper.Column(
        'password',
        ('allowedHost', 'credential', 'password',),
        """
allowedVirtualGuests.allowedHost.credential.password
allowedHardware.allowedHost.credential.password
allowedSubnets.allowedHost.credential.password
allowedIpAddresses.allowedHost.credential.password
"""),
]


DEFAULT_COLUMNS = [
    'id',
    'name',
    'type',
    'private_ip_address',
    'host_iqn',
    'username',
    'password',
]


@click.command()
@click.argument('volume_id')
@click.option('--sortby', help='Column to sort by', default='name')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. Options: {0}'.format(
                  ', '.join(column.name for column in COLUMNS)),
              default=','.join(DEFAULT_COLUMNS))
@environment.pass_env
def cli(env, columns, sortby, volume_id):
    """List ACLs."""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    access_list = block_manager.get_block_volume_access_list(
        volume_id=volume_id)
    table = formatting.Table(columns.columns)
    table.sortby = sortby

    for key, type_name in [('allowedVirtualGuests', 'VIRTUAL'),
                           ('allowedHardware', 'HARDWARE'),
                           ('allowedSubnets', 'SUBNET'),
                           ('allowedIpAddresses', 'IP')]:
        for obj in access_list.get(key, []):
            obj['type'] = type_name
            table.add_row([value or formatting.blank()
                           for value in columns.row(obj)])

    env.fout(table)
