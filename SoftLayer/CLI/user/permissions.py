"""List a users permissions."""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """User Permissions.

    Some permissions here may also be managed by IBM IAM service.
    See https://cloud.ibm.com/docs/account?topic=account-migrated_permissions for more details.
    """

    mgr = SoftLayer.UserManager(env.client)
    user_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'username')
    object_mask = "mask[id, permissions, isMasterUserFlag, roles]"

    user = mgr.get_user(user_id, object_mask)
    all_permissions = mgr.get_permission_departments()

    user_permissions = perms_to_dict(user['permissions'])
    all_table = formatting.KeyValueTable(['Department', 'Permissions'])
    if user['isMasterUserFlag']:
        click.secho('This account is the Master User and has all permissions enabled', fg='green')

    env.fout(roles_table(user))
    for department in all_permissions:
        all_table.add_row([
            department.get('name'),
            permission_table(user_permissions, department.get('permissions', []))
        ])
    env.fout(all_table)


def perms_to_dict(perms):
    """Takes a list of permissions and transforms it into a dictionary for better searching"""
    permission_dict = {}
    for perm in perms:
        permission_dict[perm['keyName']] = True
    return permission_dict


def permission_table(user_permissions, all_permissions):
    """Creates a table of available permissions"""

    table = formatting.Table(['KeyName', 'Assigned', 'Description'])
    table.align['KeyName'] = 'l'
    table.align['Description'] = 'l'
    table.align['Assigned'] = 'l'
    for perm in all_permissions:
        assigned = user_permissions.get(perm['keyName'], False)
        table.add_row([perm['keyName'], assigned, perm['description']])
    return table


def roles_table(user):
    """Creates a table for a users roles"""
    table = formatting.Table(['id', 'Role Name', 'Description'])
    for role in user['roles']:
        table.add_row([role['id'], role['name'], role['description']])
    return table
