"""Metric Utilities"""
import datetime
import itertools
import sys

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


from pprint import pprint as pp

@click.command(short_help="""Report on Resources in closing datacenters""")
@environment.pass_env
def cli(env):
    """Report on Resources in closing datacenters

    Displays a list of Datacenters soon to be shutdown, and any resources on the account 
in those locations
    """

    closing_filter = {
        'capabilities': {
            'operation': 'in',
            'options': [{'name': 'data', 'value': ['CLOSURE_ANNOUNCED']}]
        },
        'name': {
            'operation': 'orderBy',
            'options': [{'name': 'sort', 'value': ['DESC']}]
        }
    }
    mask = """mask[name, datacenterLongName, frontendRouterId, capabilities, datacenterId, backendRouterId,
backendRouterName, frontendRouterName]"""
    closing_pods = env.client.call('SoftLayer_Network_Pod', 'getAllObjects', mask=mask)
    # Find all VLANs in the POD that is going to close.
    search = "_objectType:SoftLayer_Network_Vlan  primaryRouter.hostname: \"{}\" || primaryRouter.hostname: \"{}\""
    resource_mask = """mask[
        resource(SoftLayer_Network_Vlan)[
            id,fullyQualifiedName,name,note,vlanNumber,networkSpace,
            virtualGuests[id,fullyQualifiedDomainName,billingItem[cancellationDate]],
            hardware[id,fullyQualifiedDomainName,billingItem[cancellationDate]],
            networkVlanFirewall[id,primaryIpAddress,billingItem[cancellationDate]],
            privateNetworkGateways[id,name,networkSpace],
            publicNetworkGateways[id,name,networkSpace]
        ]
    ]
    """
    table_title = "Resources in closing datacenters"
    resource_table = formatting.Table(["Id", "Name", "Public VLAN", "Private VLAN", "Type", "Datacenter",
                                       "POD", "Cancellation Date"], title=table_title)
    resource_table.align = 'l'
    for pod in closing_pods:
        resources = {'hardware': {}, 'virtual': {}, 'firewall': {}, 'gateway': {}}
        vlans = env.client.call('SoftLayer_Search', 'advancedSearch',
                                    search.format(pod.get('backendRouterName'), pod.get('frontendRouterName')),
                                    iter=True, mask=resource_mask)
        for vlan in vlans:
            resources = process_vlan(vlan.get('resource', {}), resources)
        
        for resource_type in resources.keys():
            
            for resource_object in resources[resource_type].values():
                resource_table.add_row([
                    resource_object['id'],
                    resource_object['name'],
                    resource_object['vlan'].get('PUBLIC', '-'),
                    resource_object['vlan'].get('PRIVATE', '-'),
                    resource_type,
                    pod.get('datacenterLongName'),
                    pod.get('backendRouterName'),
                    resource_object['cancelDate']
                ])
        
    env.fout(resource_table)


# returns a Table Row for a given resource
def process_vlan(vlan, resources=None):
    if resources is None:
        resources = {'hardware': {}, 'virtual': {}, 'firewall': {}, 'gateway': {}}

    type_x = "virtual"
    for x in vlan.get('virtualGuests', {}):
        existing = resources[type_x].get(x.get('id'))
        resources[type_x][x['id']] = build_resource_object('fullyQualifiedDomainName', vlan, x, existing)

    type_x = 'hardware'
    for x in vlan.get('hardware', {}):
        existing = resources[type_x].get(x.get('id'))
        resources[type_x][x['id']] = build_resource_object('fullyQualifiedDomainName', vlan, x, existing)

    type_x = 'firewall'
    for x in vlan.get('networkVlanFirewall', {}):
        existing = resources[type_x].get(x.get('id'))
        resources[type_x][x['id']] = build_resource_object('primaryIpAddress', vlan, x, existing)

    type_x = 'gateway'
    for x in vlan.get('privateNetworkGateways', {}):
        existing = resources[type_x].get(x.get('id'))
        resources[type_x][x['id']] = build_resource_object('name', vlan, x, existing)
    for x in vlan.get('publicNetworkGateways', {}):
        existing = resources[type_x].get(x.get('id'))
        resources[type_x][x['id']] = build_resource_object('name', vlan, x, existing)

    return resources

# name_property is what property to use as the name from resource
# vlan is the vlan object
# resource has the data we want
# entry is for any existing data
def build_resource_object(name_property, vlan, resource, entry):
    new_entry  = {
        'id': resource.get('id'),
        'name': resource.get(name_property),
        'vlan': {vlan.get('networkSpace'): vlan.get('vlanNumber')},
        'cancelDate': utils.clean_time(utils.lookup(resource, 'billingItem', 'cancellationDate'))
    }
    if entry:
        entry['vlan'][vlan.get('networkSpace')] = vlan.get('vlanNumber')
    else:
        entry = new_entry

    return entry