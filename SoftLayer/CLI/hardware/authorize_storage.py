"""Authorize File or Block Storage to a Hardware Server"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--username-storage', '-u', type=click.STRING,
              help="The storage username to be added to the hardware server")
@environment.pass_env
def cli(env, identifier, username_storage):
    """Authorize File or Block Storage to a Hardware Server."""
    hardware = SoftLayer.HardwareManager(env.client)
    hardware_id = helpers.resolve_id(hardware.resolve_ids, identifier, 'hardware')

    if not hardware.authorize_storage(hardware_id, username_storage):
        raise exceptions.CLIAbort('Authorize Storage Failed')
    env.fout('Successfully Storage Added.')
