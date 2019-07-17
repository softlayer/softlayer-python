"""List options for creating Placement Groups"""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.vs_placement import PlacementManager as PlacementManager


@click.command()
@environment.pass_env
def cli(env):
    """List options for creating a placement group."""
    manager = PlacementManager(env.client)

    routers = manager.get_routers()
    env.fout(get_router_table(routers))

    rules = manager.get_all_rules()
    env.fout(get_rule_table(rules))


def get_router_table(routers):
    """Formats output from _get_routers and returns a table. """
    table = formatting.Table(['Datacenter', 'Hostname', 'Backend Router Id'], "Available Routers")
    for router in routers:
        datacenter = router['topLevelLocation']['longName']
        table.add_row([datacenter, router['hostname'], router['id']])
    return table


def get_rule_table(rules):
    """Formats output from get_all_rules and returns a table. """
    table = formatting.Table(['Id', 'KeyName'], "Rules")
    for rule in rules:
        table.add_row([rule['id'], rule['keyName']])
    return table
