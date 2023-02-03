"""Report on Resources in closing datacenters"""
import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command(cls=SLCommand, short_help="""Report on Resources in closing datacenters""")
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
    closing_pods = env.client.call('SoftLayer_Network_Pod', 'getAllObjects', mask=mask, filter=closing_filter)
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
        # Go through the vlans and coalate the resources into a data structure that is easy to print out
        for vlan in vlans:
            resources = process_vlan(vlan.get('resource', {}), resources)

        # Go through each resource and add it to the table
        for resource_type, resource_values in resources.items():
            for resource_id, resource_object in resource_values.items():
                resource_table.add_row([
                    resource_id,
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
    """Takes in a vlan object and pulls out the needed resources"""
    if resources is None:
        resources = {'hardware': {}, 'virtual': {}, 'firewall': {}, 'gateway': {}}

    type_x = "virtual"
    for obj_x in vlan.get('virtualGuests', {}):
        existing = resources[type_x].get(obj_x.get('id'))
        resources[type_x][obj_x['id']] = build_resource_object('fullyQualifiedDomainName', vlan, obj_x, existing)

    type_x = 'hardware'
    for obj_x in vlan.get('hardware', {}):
        existing = resources[type_x].get(obj_x.get('id'))
        resources[type_x][obj_x['id']] = build_resource_object('fullyQualifiedDomainName', vlan, obj_x, existing)

    type_x = 'firewall'
    for obj_x in vlan.get('networkVlanFirewall', {}):
        existing = resources[type_x].get(obj_x.get('id'))
        resources[type_x][obj_x['id']] = build_resource_object('primaryIpAddress', vlan, obj_x, existing)

    type_x = 'gateway'
    for obj_x in vlan.get('privateNetworkGateways', {}):
        existing = resources[type_x].get(obj_x.get('id'))
        resources[type_x][obj_x['id']] = build_resource_object('name', vlan, obj_x, existing)
    for obj_x in vlan.get('publicNetworkGateways', {}):
        existing = resources[type_x].get(obj_x.get('id'))
        resources[type_x][obj_x['id']] = build_resource_object('name', vlan, obj_x, existing)

    return resources


def build_resource_object(name_property, vlan, resource, entry):
    """builds out a resource object and puts the required values in the right place.

    :param: name_property is what property to use as the name from resource
    :param: vlan is the vlan object
    :param: resource has the data we want
    :param: entry is for any existing data
    """
    new_entry = {
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
