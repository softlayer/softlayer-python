"""Edit a specific reserved capacity."""
# :license: MIT, see LICENSE for more details.

import click
from click import INT, STRING

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--name', '-n', type=STRING, help="Name of the Reserved Capacity to be edited")
@environment.pass_env
def cli(env, identifier, name):
    """Edit a specific reserved capacity."""
    reserved_manager = SoftLayer.ReservedCapacityManager(env.client)
    reserved_id = helpers.resolve_id(reserved_manager.resolve_ids, identifier, 'Reserved Capacity')

    reserved_result = reserved_manager.edit(reserved_id, name)

    if reserved_result:
        click.secho("The Reserved Capacity %s was edited successfully" % identifier, fg='green')
    else:
        click.secho("Failed to edit the Reserved Capacity %s" % identifier, fg='red')

