"""Detail firewall."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import firewall
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Detail firewall."""

    mgr = SoftLayer.FirewallManager(env.client)

    firewall_type, firewall_id = firewall.parse_id(identifier)
    _firewall = mgr.get_instance(firewall_id)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', _firewall.get('id')])
    table.add_row(['primaryIpAddress', _firewall.get('primaryIpAddress')])
    table.add_row(['datacenter', utils.lookup(_firewall, 'datacenter', 'longName')])
    table.add_row(['networkVlan', utils.lookup(_firewall, 'networkVlan', 'name')])
    table.add_row(['networkVlaniD', utils.lookup(_firewall, 'networkVlan', 'id')])

    if firewall_type == 'vlan':
        rules = mgr.get_dedicated_fwl_rules(firewall_id)
    else:
        rules = mgr.get_standard_fwl_rules(firewall_id)
    table.add_row(['rules', get_rules_table(rules)])
    env.fout(table)


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
            utils.lookup(rule, 'sourceIpSubnetMask'),
            '%s:%s-%s' % (rule['destinationIpAddress'],
                          rule['destinationPortRangeStart'],
                          rule['destinationPortRangeEnd']),
            utils.lookup(rule, 'destinationIpSubnetMask')])
    return table
