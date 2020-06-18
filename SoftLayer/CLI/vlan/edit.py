"""Edit a vlan's details."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment, exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--name', '-n',
              help="The optional name for this VLAN")
@click.option('--note', '-e',
              help="The note for this vlan.")
@click.option('--tags', '-g',
              multiple=True,
              help='Tags to set e.g. "tag1,tag2", or empty string to remove all'
              )
@environment.pass_env
def cli(env, identifier, name, note, tags):
    """Edit a vlan's details."""

    data = {
        'name': name,
        'note': note
    }

    if tags:
        data['tags'] = ','.join(tags)

    mgr = SoftLayer.NetworkManager(env.client)
    vlan_id = helpers.resolve_id(mgr.resolve_vlan_ids, identifier, 'VLAN')
    vlan = mgr.edit(vlan_id, **data)

    if vlan:
        click.secho("Vlan edited successfully", fg='green')
    else:
        click.secho("Failed to edit the vlan", fg='red')
