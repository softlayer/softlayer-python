"""User details."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@click.option('--keys', '-k', is_flag=True, default=False,
              help="Show the users API key.")
@click.option('--permissions', '-p', is_flag=True, default=False,
              help="Display permissions assigned to this user. Master users will show no permissions")
@click.option('--hardware', '-h', is_flag=True, default=False,
              help="Display hardware this user has access to.")
@click.option('--virtual', '-v', is_flag=True, default=False,
              help="Display virtual guests this user has access to.")
@click.option('--logins', '-l', is_flag=True, default=False,
              help="Show login history of this user for the last 30 days")
@click.option('--events', '-e', is_flag=True, default=False,
              help="Show audit log for this user.")
@environment.pass_env
def cli(env, identifier, keys, permissions, hardware, virtual, logins, events):
    """User details."""

    mgr = SoftLayer.UserManager(env.client)
    user_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'username')
    object_mask = "userStatus[name], parent[id, username], apiAuthenticationKeys[authenticationKey], "\
                  "unsuccessfulLogins, successfulLogins"

    user = mgr.get_user(user_id, object_mask)
    env.fout(basic_info(user, keys))

    if permissions:
        perms = mgr.get_user_permissions(user_id)
        env.fout(print_permissions(perms))
    if hardware:
        mask = "id, hardware, dedicatedHosts"
        access = mgr.get_user(user_id, mask)
        env.fout(print_dedicated_access(access.get('dedicatedHosts', [])))
        env.fout(print_access(access.get('hardware', []), 'Hardware'))
    if virtual:
        mask = "id, virtualGuests"
        access = mgr.get_user(user_id, mask)
        env.fout(print_access(access.get('virtualGuests', []), 'Virtual Guests'))
    if logins:
        login_log = mgr.get_logins(user_id)
        env.fout(print_logins(login_log))
    if events:
        event_log = mgr.get_events(user_id)
        env.fout(print_events(event_log))


def basic_info(user, keys):
    """Prints a table of basic user information"""

    table = formatting.KeyValueTable(['Title', 'Basic Information'])
    table.align['Title'] = 'r'
    table.align['Basic Information'] = 'l'

    table.add_row(['Id', user.get('id', '-')])
    table.add_row(['Username', user.get('username', '-')])
    if keys:
        for key in user.get('apiAuthenticationKeys'):
            table.add_row(['APIKEY', key.get('authenticationKey')])
    table.add_row(['Name', "%s %s" % (user.get('firstName', '-'), user.get('lastName', '-'))])
    table.add_row(['Email', user.get('email')])
    table.add_row(['OpenID', user.get('openIdConnectUserName')])
    address = "%s %s %s %s %s %s" % (
        user.get('address1'), user.get('address2'), user.get('city'), user.get('state'),
        user.get('country'), user.get('postalCode'))
    table.add_row(['Address', address])
    table.add_row(['Company', user.get('companyName')])
    table.add_row(['Created', user.get('createDate')])
    table.add_row(['Phone Number', user.get('officePhone')])
    if user.get('parentId', False):
        table.add_row(['Parent User', utils.lookup(user, 'parent', 'username')])
    table.add_row(['Status', utils.lookup(user, 'userStatus', 'name')])
    table.add_row(['PPTP VPN', user.get('pptpVpnAllowedFlag', 'No')])
    table.add_row(['SSL VPN', user.get('sslVpnAllowedFlag', 'No')])
    for login in user.get('unsuccessfulLogins', {}):
        login_string = "%s From: %s" % (login.get('createDate'), login.get('ipAddress'))
        table.add_row(['Last Failed Login', login_string])
        break
    for login in user.get('successfulLogins', {}):
        login_string = "%s From: %s" % (login.get('createDate'), login.get('ipAddress'))
        table.add_row(['Last Login', login_string])
        break

    return table


def print_permissions(permissions):
    """Prints out a users permissions"""

    table = formatting.Table(['keyName', 'Description'])
    for perm in permissions:
        table.add_row([perm['keyName'], perm['name']])
    return table


def print_access(access, title):
    """Prints out the hardware or virtual guests a user can access"""

    columns = ['id', 'hostname', 'Primary Public IP', 'Primary Private IP', 'Created']
    table = formatting.Table(columns, title)

    for host in access:
        host_id = host.get('id')
        host_fqdn = host.get('fullyQualifiedDomainName', '-')
        host_primary = host.get('primaryIpAddress')
        host_private = host.get('primaryBackendIpAddress')
        host_created = host.get('provisionDate')
        table.add_row([host_id, host_fqdn, host_primary, host_private, host_created])
    return table


def print_dedicated_access(access):
    """Prints out the dedicated hosts a user can access"""

    table = formatting.Table(['id', 'Name', 'Cpus', 'Memory', 'Disk', 'Created'], 'Dedicated Access')
    for host in access:
        host_id = host.get('id')
        host_fqdn = host.get('name')
        host_cpu = host.get('cpuCount')
        host_mem = host.get('memoryCapacity')
        host_disk = host.get('diskCapacity')
        host_created = host.get('createDate')
        table.add_row([host_id, host_fqdn, host_cpu, host_mem, host_disk, host_created])
    return table


def print_logins(logins):
    """Prints out the login history for a user"""
    table = formatting.Table(['Date', 'IP Address', 'Successufl Login?'])
    for login in logins:
        table.add_row([login.get('createDate'), login.get('ipAddress'), login.get('successFlag')])
    return table


def print_events(events):
    """Prints out the event log for a user"""
    columns = ['Date', 'Type', 'IP Address', 'label', 'username']
    table = formatting.Table(columns)
    for event in events:
        table.add_row([event.get('eventCreateDate'), event.get('eventName'),
                       event.get('ipAddress'), event.get('label'), event.get('username')])
    return table
