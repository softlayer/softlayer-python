"""Delete a placement group."""

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.managers.vs import VSManager as VSManager
from SoftLayer.managers.vs_placement import PlacementManager as PlacementManager


@click.command(epilog="Once provisioned, virtual guests can be managed with the slcli vs commands")
@click.argument('identifier')
@click.option('--purge', is_flag=True,
              help="Delete all guests in this placement group. "
                   "The group itself can be deleted once all VMs are fully reclaimed")
@environment.pass_env
def cli(env, identifier, purge):
    """Delete a placement group.

    Placement Group MUST be empty before you can delete it.

    IDENTIFIER can be either the Name or Id of the placement group you want to view
    """
    manager = PlacementManager(env.client)
    group_id = helpers.resolve_id(manager.resolve_ids, identifier, 'placement_group')

    if purge:
        placement_group = manager.get_object(group_id)
        guest_list = ', '.join([guest['fullyQualifiedDomainName'] for guest in placement_group['guests']])
        if len(placement_group['guests']) < 1:
            raise exceptions.CLIAbort('No virtual servers were found in placement group %s' % identifier)

        click.secho("You are about to delete the following guests!\n%s" % guest_list, fg='red')
        if not (env.skip_confirmations or formatting.confirm("This action will cancel all guests! Continue?")):
            raise exceptions.CLIAbort('Aborting virtual server order.')
        vm_manager = VSManager(env.client)
        for guest in placement_group['guests']:
            click.secho("Deleting %s..." % guest['fullyQualifiedDomainName'])
            vm_manager.cancel_instance(guest['id'])
        return

    click.secho("You are about to delete the following placement group! %s" % identifier, fg='red')
    if not (env.skip_confirmations or formatting.confirm("This action will cancel the placement group! Continue?")):
        raise exceptions.CLIAbort('Aborting virtual server order.')
    cancel_result = manager.delete(group_id)
    if cancel_result:
        click.secho("Placement Group %s has been canceld." % identifier, fg='green')
