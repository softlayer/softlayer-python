"""Capture virtual server image."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


# pylint: disable=redefined-builtin

@click.command(short_help="Capture SoftLayer image.")
@click.argument('identifier')
@click.option('--name', '-n', required=True, help="Name of the image")
@click.option('--all', help="Capture all disks belonging to the VS")
@click.option('--note', help="Add a note to be associated with the image")
@environment.pass_env
def cli(env, identifier, name, all, note):
    """Capture one or all disks from a virtual server to a SoftLayer image."""

    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')

    capture = vsi.capture(vs_id, name, all, note)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['vs_id', capture['guestId']])
    table.add_row(['date', capture['createDate'][:10]])
    table.add_row(['time', capture['createDate'][11:19]])
    table.add_row(['transaction', formatting.transaction_status(capture)])
    table.add_row(['transaction_id', capture['id']])
    table.add_row(['all_disks', all])
    env.fout(table)
