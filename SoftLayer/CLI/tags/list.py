"""List Tags."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.exceptions import SoftLayerAPIError
from SoftLayer.managers.tags import TagManager
from SoftLayer import utils

# pylint: disable=unnecessary-lambda


@click.command()
@click.option('--detail', '-d', is_flag=True, default=False,
              help="Show information about the resources using this tag.")
@environment.pass_env
def cli(env, detail):
    """List Tags."""

    tag_manager = TagManager(env.client)

    if detail:
        tables = detailed_table(tag_manager, tag_manager.get_attached_tags())
        for table in tables:
            env.fout(table)
    else:
        table = simple_table(tag_manager)
        env.fout(table)
    # pp(tags.list_tags())


def tag_row(tag):
    """Format a tag table row"""
    return [tag.get('id'), tag.get('name'), tag.get('referenceCount', 0)]


def detailed_table(tag_manager, tags):
    """Creates a table for each tag, with details about resources using it"""
    tables = []
    for tag in tags:
        references = tag_manager.get_tag_references(tag.get('id'))
        # pp(references)
        new_table = formatting.Table(['Id', 'Type', 'Resource'], title=tag.get('name'))
        for reference in references:
            tag_type = utils.lookup(reference, 'tagType', 'keyName')
            resource_id = reference.get('resourceTableId')
            resource_row = get_resource_name(tag_manager, resource_id, tag_type)
            new_table.add_row([resource_id, tag_type, resource_row])
        tables.append(new_table)

    return tables


def simple_table(tag_manager):
    """Just tags and how many resources on each"""
    tags = tag_manager.list_tags()
    table = formatting.Table(['Id', 'Tag', 'Count'], title='Tags')
    for tag in tags.get('attached', []):
        table.add_row(tag_row(tag))
    for tag in tags.get('unattached', []):
        table.add_row(tag_row(tag))
    return table


def get_resource_name(tag_manager, resource_id, tag_type):
    """Returns a string to identify a resource"""
    name = None
    try:
        resource = tag_manager.reference_lookup(resource_id, tag_type)
        name = tag_manager.get_resource_name(resource, tag_type)
    except SoftLayerAPIError as exception:
        name = "{}".format(exception.reason)
    return name
