"""Detail firewall."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import firewall
from SoftLayer.CLI import formatting


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Detail firewall."""

    mgr = SoftLayer.FirewallManager(env.client)

    firewall_type, firewall_id = firewall.parse_id(identifier)
    if firewall_type == 'vlan':
        rules = mgr.get_dedicated_fwl_rules(firewall_id)
    else:
        rules = mgr.get_standard_fwl_rules(firewall_id)

    env.fout(get_rules_table(rules))


def get_rules_table(rules):
    """Helper to format the rules into a table.

    :param list rules: A list containing the rules of the firewall
    :returns: a formatted table of the firewall rules
    """
    table = formatting.Table(['#', 'action', 'protocol', 'src_ip', 'src_mask',
                              'dest', 'dest_mask'])
    table.sortby = '#'
    for rule in rules:
        table.add_row([
            rule['orderValue'],
            rule['action'],
            rule['protocol'],
            rule['sourceIpAddress'],
            rule['sourceIpSubnetMask'],
            '%s:%s-%s' % (rule['destinationIpAddress'],
                          rule['destinationPortRangeStart'],
                          rule['destinationPortRangeEnd']),
            rule['destinationIpSubnetMask']])
    return table
