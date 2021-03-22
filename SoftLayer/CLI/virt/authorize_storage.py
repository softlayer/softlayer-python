"""Authorize File, Block and Portable Storage to a Virtual Server"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--username-storage', '-u', type=click.STRING,
              help="The storage username to be added to the virtual server")
@click.option('--portable-id', type=click.INT,
              help="The portable storage id to be added to the virtual server")
@environment.pass_env
def cli(env, identifier, username_storage, portable_id):
    """Authorize File, Block and Portable Storage to a Virtual Server.
    """
    vs = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vs.resolve_ids, identifier, 'vs')
    table = formatting.KeyValueTable(['name', 'value'], title="Portable Storage Detail")
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    if username_storage:
        if not vs.authorize_storage(vs_id, username_storage):
            raise exceptions.CLIAbort('Authorize Volume Failed')
        env.fout('Successfully Volume: %s was Added.' % username_storage)
    if portable_id:
        portable_id = helpers.resolve_id(vs.resolve_ids, portable_id, 'storage')
        portable_result = vs.attach_portable_storage(vs_id, portable_id)

        env.fout('Successfully Portable Storage: %i was Added.' % portable_id)

        table.add_row(['Id', portable_result['id']])
        table.add_row(['createDate', portable_result['createDate']])
        env.fout(table)
