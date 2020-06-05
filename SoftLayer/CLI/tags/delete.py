"""List Tags."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.exceptions import SoftLayerAPIError
from SoftLayer.managers.tags import TagManager
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils

# pylint: disable=unnecessary-lambda

from pprint import pprint as pp


@click.command()
@click.option('-id', required=False, show_default=False, type=int, help='identifier')
@click.option('--name', required=False, default=False, type=str, show_default=False, help='tag name')
@environment.pass_env
def cli(env, id, name):
    """delete Tag."""

    tag_manager = TagManager(env.client)

    if not name and id is not None:
        tag_name = tag_manager.get_tag(id)
        tag_manager.delete_tag(tag_name['name'])
    if name and id is None:
        tag_manager.delete_tag(name)
