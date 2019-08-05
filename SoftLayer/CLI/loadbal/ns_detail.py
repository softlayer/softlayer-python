"""Get Netscaler details."""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get Netscaler details."""
    mgr = SoftLayer.LoadBalancerManager(env.client)

    this_lb = mgr.get_adc(identifier)
    table = netscaler_table(this_lb)
    env.fout(table)


def netscaler_table(this_lb):
    """Formats the netscaler info table"""
    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['Id', this_lb.get('id')])
    table.add_row(['Type', this_lb.get('description')])
    table.add_row(['Name', this_lb.get('name')])
    table.add_row(['Location', utils.lookup(this_lb, 'datacenter', 'longName')])
    table.add_row(['Managment Ip', this_lb.get('managementIpAddress')])
    table.add_row(['Root Password', utils.lookup(this_lb, 'password', 'password')])
    table.add_row(['Primary Ip', this_lb.get('primaryIpAddress')])
    table.add_row(['License Expiration', utils.clean_time(this_lb.get('licenseExpirationDate'))])
    subnet_table = formatting.Table(['Id', 'Subnet', 'Type', 'Space'])
    for subnet in this_lb.get('subnets', []):
        subnet_table.add_row([
            subnet.get('id'),
            "{}/{}".format(subnet.get('networkIdentifier'), subnet.get('cidr')),
            subnet.get('subnetType'),
            subnet.get('addressSpace')
        ])
    table.add_row(['Subnets', subnet_table])

    vlan_table = formatting.Table(['Id', 'Number'])
    for vlan in this_lb.get('networkVlans', []):
        vlan_table.add_row([vlan.get('id'), vlan.get('vlanNumber')])
    table.add_row(['Vlans', vlan_table])

    return table
