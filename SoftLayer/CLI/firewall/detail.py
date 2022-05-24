"""Detail firewall."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import firewall
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--credentials', type=click.BOOL,
              help="Display FortiGate username and FortiGate password to multi vlans.")
@environment.pass_env
def cli(env, identifier, credentials):
    """Detail firewall."""

    mgr = SoftLayer.FirewallManager(env.client)

    firewall_type, firewall_id = firewall.parse_id(identifier)

    if firewall_type == 'vs' or firewall_type == 'server' or firewall_type == 'vlan' or firewall_type == 'multiVlan':

        if firewall_type == 'vlan':
            _firewall = mgr.get_instance(firewall_id)

            table = formatting.KeyValueTable(['name', 'value'])
            table.align['name'] = 'r'
            table.align['value'] = 'l'

            table.add_row(['id', _firewall.get('id')])
            table.add_row(['primaryIpAddress', _firewall.get('primaryIpAddress')])
            table.add_row(['datacenter', utils.lookup(_firewall, 'datacenter', 'longName')])
            table.add_row(['networkVlan', utils.lookup(_firewall, 'networkVlan', 'name')])
            table.add_row(['networkVlaniD', utils.lookup(_firewall, 'networkVlan', 'id')])

            rules = mgr.get_dedicated_fwl_rules(firewall_id)
            table.add_row(['rules', get_rules_table(rules)])

        if firewall_type == 'multiVlan':
            _firewall = mgr.get_instance(firewall_id)

            table = formatting.KeyValueTable(['name', 'value'])
            table.align['name'] = 'r'
            table.align['value'] = 'l'

            table.add_row(['name', utils.lookup(_firewall, 'networkGateway', 'name')])
            table.add_row(['datacenter', utils.lookup(_firewall, 'datacenter', 'longName')])
            table.add_row(['public ip', utils.lookup(_firewall, 'networkGateway', 'publicIpAddress', 'ipAddress')])
            table.add_row(['private ip', utils.lookup(_firewall, 'networkGateway', 'privateIpAddress', 'ipAddress')])
            table.add_row(['public  ipv6', utils.lookup(_firewall, 'networkGateway', 'publicIpv6Address', 'ipAddress')])
            table.add_row(['public vlan', utils.lookup(_firewall, 'networkGateway', 'publicVlan', 'vlanNumber')])
            table.add_row(['private vlan', utils.lookup(_firewall, 'networkGateway', 'privateVlan', 'vlanNumber')])
            table.add_row(['type', _firewall.get('firewallType')])

            if credentials:
                table.add_row(['FortiGate username', utils.lookup(_firewall, 'managementCredentials', 'username')])
                table.add_row(['FortiGate password', utils.lookup(_firewall, 'managementCredentials', 'password')])

            rules = mgr.get_dedicated_fwl_rules(firewall_id)
            table.add_row(['rules', get_rules_table(rules)])

        if firewall_type == 'vs' or firewall_type == 'server':
            rules = mgr.get_standard_fwl_rules(firewall_id)
            table = get_rules_table(rules)

        env.fout(table)

    else:
        click.secho('Invalid firewall type %s: firewall type should be either vlan, multiVlan, vs or server.'
                    % firewall_type, fg='red')
        return


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
