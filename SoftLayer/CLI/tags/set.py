"""Set Tags."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.managers.tags import TagManager


@click.command()
@click.option('--tags', '-t', type=click.STRING, required=True,
              help='Comma seperated list of tags, enclosed in quotes. "tag1, tag2"')
@click.option('--key-name', '-k', type=click.STRING, required=True,
              help="Key name of a tag type e.g. GUEST, HARDWARE. See slcli tags taggable output.")
@click.option('--resource-id', '-r', type=click.INT, required=True, help="ID of the object being tagged")
@environment.pass_env
def cli(env, tags, key_name, resource_id):
    """Set Tags."""

    tag_manager = TagManager(env.client)
    tags = tag_manager.set_tags(tags, key_name, resource_id)

    if tags:
        click.secho("Set tags successfully", fg='green')
    else:
        click.secho("Failed to set tags", fg='red')
