"""List everything that could be tagged."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.tags import TagManager


@click.command()
@environment.pass_env
def cli(env):
    """List everything that could be tagged."""

    tag_manager = TagManager(env.client)
    tag_types = tag_manager.get_all_tag_types()
    for tag_type in tag_types:
        title = "{} ({})".format(tag_type['description'], tag_type['keyName'])
        table = formatting.Table(['Id', 'Name'], title=title)
        resources = tag_manager.taggable_by_type(tag_type['keyName'])
        for resource in resources:
            table.add_row([
                resource['resource']['id'],
                tag_manager.get_resource_name(resource['resource'], tag_type['keyName'])
            ])
        env.fout(table)
