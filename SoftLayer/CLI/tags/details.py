"""Details of a Tag."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI.tags.list import detailed_table
from SoftLayer.managers.tags import TagManager


@click.command()
@click.argument('identifier')
@click.option('--name', required=False, default=False, is_flag=True, show_default=False,
              help='Assume identifier is a tag name. Useful if your tag name is a number.')
@environment.pass_env
def cli(env, identifier, name):
    """Get details for a Tag. Identifier can be either a name or tag-id"""

    tag_manager = TagManager(env.client)

    # If the identifier is a int, and user didn't tell us it was a name.
    if str.isdigit(identifier) and not name:
        tags = [tag_manager.get_tag(identifier)]
    else:
        tags = tag_manager.get_tag_by_name(identifier)
    table = detailed_table(tag_manager, tags)
    env.fout(table)
