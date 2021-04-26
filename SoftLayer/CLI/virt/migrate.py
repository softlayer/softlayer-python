"""Manage Migrations of Virtual Guests"""
# :license: MIT, see LICENSE for more details.
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command()
@click.option('--guest', '-g', type=click.INT, help="Guest ID to immediately migrate.")
@click.option('--all', '-a', 'migrate_all', is_flag=True, default=False,
              help="Migrate ALL guests that require migration immediately.")
@click.option('--host', '-h', type=click.INT,
              help="Dedicated Host ID to migrate to. Only works on guests that are already on a dedicated host.")
@environment.pass_env
def cli(env, guest, migrate_all, host):
    """Manage VSIs that require migration. Can migrate Dedicated Host VSIs as well."""

    vsi = SoftLayer.VSManager(env.client)
    pending_filter = {'virtualGuests': {'pendingMigrationFlag': {'operation': 1}}}
    dedicated_filter = {'virtualGuests': {'dedicatedHost': {'id': {'operation': 'not null'}}}}
    mask = """mask[
                id, hostname, domain, datacenter, pendingMigrationFlag, powerState,
                primaryIpAddress,primaryBackendIpAddress, dedicatedHost
            ]"""

    # No options, just print out a list of guests that can be migrated
    if not (guest or migrate_all):
        require_migration = vsi.list_instances(filter=pending_filter, mask=mask)
        require_table = formatting.Table(['id', 'hostname', 'domain', 'datacenter'], title="Require Migration")

        for vsi_object in require_migration:
            require_table.add_row([
                vsi_object.get('id'),
                vsi_object.get('hostname'),
                vsi_object.get('domain'),
                utils.lookup(vsi_object, 'datacenter', 'name')
            ])

        if require_migration:
            env.fout(require_table)
        else:
            click.secho("No guests require migration at this time", fg='green')

        migrateable = vsi.list_instances(filter=dedicated_filter, mask=mask)
        migrateable_table = formatting.Table(['id', 'hostname', 'domain', 'datacenter', 'Host Name', 'Host Id'],
                                             title="Dedicated Guests")
        for vsi_object in migrateable:
            migrateable_table.add_row([
                vsi_object.get('id'),
                vsi_object.get('hostname'),
                vsi_object.get('domain'),
                utils.lookup(vsi_object, 'datacenter', 'name'),
                utils.lookup(vsi_object, 'dedicatedHost', 'name'),
                utils.lookup(vsi_object, 'dedicatedHost', 'id')
            ])
        env.fout(migrateable_table)
    # Migrate all guests with pendingMigrationFlag=True
    elif migrate_all:
        require_migration = vsi.list_instances(filter=pending_filter, mask="mask[id]")
        if not require_migration:
            click.secho("No guests require migration at this time", fg='green')
        for vsi_object in require_migration:
            migrate(vsi, vsi_object['id'])
    # Just migrate based on the options
    else:
        migrate(vsi, guest, host)


def migrate(vsi_manager, vsi_id, host_id=None):
    """Handles actually migrating virtual guests and handling the exception"""

    try:
        if host_id:
            vsi_manager.migrate_dedicated(vsi_id, host_id)
        else:
            vsi_manager.migrate(vsi_id)
        click.secho("Started a migration on {}".format(vsi_id), fg='green')
    except SoftLayer.exceptions.SoftLayerAPIError as ex:
        click.secho("Failed to migrate {}. {}".format(vsi_id, str(ex)), fg='red')
