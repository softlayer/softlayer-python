"""Delete Tags."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.managers.tags import TagManager


@click.command()
@click.argument('identifier')
@click.option('--name', required=False, default=False, is_flag=True, show_default=False,
              help='Assume identifier is a tag name. Useful if your tag name is a number.')
@environment.pass_env
def cli(env, identifier, name):
    """Delete a Tag. Tag names that contain spaces need to be encased in quotes"""

    tag_manager = TagManager(env.client)
    tag_name = identifier
    # If the identifier is a int, and user didn't tell us it was a name.
    if str.isdigit(identifier) and not name:
        tag = tag_manager.get_tag(identifier)
        tag_name = tag.get('name', None)

    result = tag_manager.delete_tag(tag_name)
    if result:
        click.secho("Tag {} has been removed".format(tag_name), fg='green')
    else:
        click.secho("Failed to remove tag {}".format(tag_name), fg='red')
