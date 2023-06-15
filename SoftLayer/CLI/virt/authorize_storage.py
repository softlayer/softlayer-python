"""Authorize File, Block and Portable Storage to a Virtual Server"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--username-storage', '-u', type=click.STRING,
              help="The storage username to be added to the virtual server")
@click.option('--portable-id', type=click.INT,
              help="The portable storage id to be added to the virtual server")
@environment.pass_env
def cli(env, identifier, username_storage, portable_id):
    """Authorize File, Block and Portable Storage to a Virtual Server."""
    virtual = SoftLayer.VSManager(env.client)
    virtual_id = helpers.resolve_id(virtual.resolve_ids, identifier, 'virtual')
    table = formatting.KeyValueTable(['name', 'value'], title="Portable Storage Detail")
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    if username_storage:
        if not virtual.authorize_storage(virtual_id, username_storage):
            raise exceptions.CLIAbort('Authorize Volume Failed')
        env.fout(f'Successfully Volume: {username_storage} was Added.')
    if portable_id:
        portable_id = helpers.resolve_id(virtual.resolve_ids, portable_id, 'storage')
        portable_result = virtual.attach_portable_storage(virtual_id, portable_id)

        env.fout(f'Successfully Portable Storage: {portable_id} was Added.')

        table.add_row(['Id', portable_result['id']])
        table.add_row(['createDate', portable_result['createDate']])
        env.fout(table)
