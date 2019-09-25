"""List Autoscale groups."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.managers.autoscale import AutoScaleManager
from SoftLayer import utils

from pprint import pprint as pp 

@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """List AutoScale Groups."""

    autoscale = AutoScaleManager(env.client)
    group = autoscale.details(identifier)
    # print(groups)
    # pp(group)
    table = formatting.KeyValueTable(["Name", "Value"])

    table.add_row(['Id', group.get('id')])
    # Ideally we would use regionalGroup->preferredDatacenter, but that generates an error.
    table.add_row(['Datacenter', group['regionalGroup']['locations'][0]['longName']])
    table.add_row(['Termination', utils.lookup(group, 'terminationPolicy', 'name')])
    table.add_row(['Minimum Members', group.get('minimumMemberCount')])
    table.add_row(['Maximum Members', group.get('maximumMemberCount')])
    table.add_row(['Current Members', group.get('virtualGuestMemberCount')])
    table.add_row(['Last Action', utils.clean_time(group.get('lastActionDate'))])
    
    for network in group.get('networkVlans'):
        network_type = utils.lookup(network, 'networkVlan', 'networkSpace')
        router = utils.lookup(network, 'networkVlan', 'primaryRouter', 'hostname')
        vlan_number = utils.lookup(network, 'networkVlan', 'vlanNumber')
        vlan_name = "{}.{}".format(router, vlan_number)
        table.add_row([network_type, vlan_name])




    env.fout(table)
