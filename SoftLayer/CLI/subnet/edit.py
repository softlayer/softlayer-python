"""Edit a subnet."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command(short_help="Edit note and tags of a subnet")
@click.argument('identifier')
@click.option('--tags', '-t', type=click.STRING,
              help='Comma separated list of tags, enclosed in quotes. "tag1, tag2"')
@click.option('--note', '-n', type=click.STRING,
              help="The note")
@environment.pass_env
def cli(env, identifier, tags, note):
    """Edit note and tags of a subnet."""

    mgr = SoftLayer.NetworkManager(env.client)
    subnet_id = helpers.resolve_id(mgr.resolve_subnet_ids, identifier,
                                   name='subnet')

    if tags:
        result = mgr.set_tags_subnet(subnet_id, tags)
        print_result(result, "Set tags")

    if note:
        result = mgr.edit_note_subnet(subnet_id, note)
        print_result(result, "Edit note")


def print_result(result, detail):
    """Prints a successfully or Failed message."""
    if result:
        click.secho("{} successfully".format(detail), fg='green')
    else:
        click.secho("Failed to {}".format(detail.lower()), fg='red')
