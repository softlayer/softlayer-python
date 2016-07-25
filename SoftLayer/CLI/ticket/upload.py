"""Adds an attachment to an existing ticket."""
# :license: MIT, see LICENSE for more details.

import os

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--path', help="The path of the attachment to be uploaded")
@click.option('--name', help="The name of the attachment shown in the ticket")
@environment.pass_env
def cli(env, identifier, path, name):
    """Adds an attachment to an existing ticket."""
    mgr = SoftLayer.TicketManager(env.client)

    ticket_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'ticket')

    if path is None:
        raise exceptions.ArgumentError("Missing argument --path")

    if not os.path.exists(path):
        raise exceptions.ArgumentError("%s not exist" % path)

    if name is None:
        name = os.path.basename(path)

    attached_file = mgr.upload_attachment(ticket_id=ticket_id,
                                          file_path=path,
                                          file_name=name)
    env.fout("File attached: \n%s" % attached_file)
