"""List images."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils

from pprint import pprint as pp





@click.command()
@click.argument('identifier')
@click.option('--keys', is_flag=True, default=False)
@environment.pass_env
def cli(env, identifier, keys):
    """User details."""
    
    mgr = SoftLayer.UserManager(env.client)
    user_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'username')
    object_mask = "userStatus[name], parent[id, username], apiAuthenticationKeys[authenticationKey], "\
                  "unsuccessfulLogins, successfulLogins"

    user = mgr.get_user(user_id, object_mask)
    env.fout(basic_info(user, keys))


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
    if user['parentId']:
        table.add_row(['Parent User', utils.lookup(user, 'parent', 'username')])
    table.add_row(['Status', utils.lookup(user, 'userStatus', 'name')])
    table.add_row(['PPTP VPN', user.get('pptpVpnAllowedFlag', 'No')])
    table.add_row(['SSL VPN', user.get('sslVpnAllowedFlag', 'No')])
    for login in  user.get('unsuccessfulLogins'):
        login_string = "%s From: %s" % (login.get('createDate'), login.get('ipAddress'))
        table.add_row(['Last Failed Login', login_string])
        break
    for login in  user.get('successfulLogins'):
        login_string = "%s From: %s" % (login.get('createDate'), login.get('ipAddress'))
        table.add_row(['Last Login', login_string])
        break

    return table

