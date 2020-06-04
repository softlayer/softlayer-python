"""Details of a Tag."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI.tags.list import detailed_table
from SoftLayer.managers.tags import TagManager


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get details for a Tag."""

    tag_manager = TagManager(env.client)

    if str.isdigit(identifier):
        tags = [tag_manager.get_tag(identifier)]
    else:
        tags = tag_manager.get_tag_by_name(identifier)
    table = detailed_table(tag_manager, tags)
    env.fout(table)
