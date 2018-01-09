"""Utility functions for use with File and Block commands."""
# :license: MIT, see LICENSE for more details.

from SoftLayer.CLI import columns as column_helper


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
        'source_subnet',
        ('allowedHost', 'sourceSubnet',),
        """
allowedVirtualGuests.allowedHost.sourceSubnet
allowedHardware.allowedHost.sourceSubnet
allowedSubnets.allowedHost.sourceSubnet
allowedIpAddresses.allowedHost.sourceSubnet
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
    column_helper.Column(
        'allowed_host_id',
        ('allowedHost', 'id',),
        """
allowedVirtualGuests.allowedHost.id
allowedHardware.allowedHost.id
allowedSubnets.allowedHost.id
allowedIpAddresses.allowedHost.id
"""),
]


DEFAULT_COLUMNS = [
    'id',
    'name',
    'type',
    'private_ip_address',
    'source_subnet',
    'host_iqn',
    'username',
    'password',
    'allowed_host_id',
]
