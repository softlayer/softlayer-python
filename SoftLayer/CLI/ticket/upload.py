"""Adds an attachment to an existing ticket."""
# :license: MIT, see LICENSE for more details.

import os

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers
from SoftLayer.CLI import ticket


@click.command()
@click.argument('identifier')
@click.option('--file', help="The path of the file to be uploaded and attached to the ticket")
@click.option('--name', help="The name of the file to be uploaded and attached to the ticket")
@environment.pass_env
def cli(env, identifier, file, name):
    """Adds an attachment to an existing ticket."""
    mgr = SoftLayer.TicketManager(env.client)

    ticket_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'ticket')

    if file is None:
        raise exceptions.ArgumentError("Missing argument --file")

    if not os.path.exists(file):
        raise exceptions.ArgumentError("%s not exist" % file)

    if name is None:
        name = os.path.basename(file)

    bytes = None
    with open(file, 'rb') as f:
        bytes = f.read()

    file_object = {
        "filename": name,
        "data": bytes
    }

    attached_file = mgr.upload_attachment(ticket_id=ticket_id, file=file_object)
    env.fout("File attached: \n%s" % attached_file)
