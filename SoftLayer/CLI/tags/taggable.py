"""List everything that could be tagged."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI.exceptions import ArgumentError
from SoftLayer.CLI import formatting
from SoftLayer.managers.tags import TagManager
from SoftLayer.CLI import environment

from pprint import pprint as pp 
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
                get_resource_name(resource['resource'], tag_type['keyName'])
            ])
        env.fout(table)


def get_resource_name(resource, tag_type):
    """Returns a string that names a resource"""
    if tag_type == 'NETWORK_VLAN_FIREWALL':
        return resource.get('primaryIpAddress')
    elif tag_type == 'NETWORK_VLAN':
        return "{} ({})".format(resource.get('vlanNumber'), resource.get('name'))
    elif tag_type == 'IMAGE_TEMPLATE' or tag_type == 'APPLICATION_DELIVERY_CONTROLLER':
        return resource.get('name')
    elif tag_type == 'TICKET':
        return resource.get('subjet')
    elif tag_type == 'NETWORK_SUBNET':
        return resource.get('networkIdentifier')
    else:
        return resource.get('fullyQualifiedDomainName')