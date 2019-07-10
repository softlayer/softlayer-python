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

    lb = mgr.get_adc(identifier)
    table = netscaler_table(lb)
    env.fout(table)


def netscaler_table(lb):
    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['Id', lb.get('id')])
    table.add_row(['Type', lb.get('description')])
    table.add_row(['Name', lb.get('name')])
    table.add_row(['Location', utils.lookup(lb, 'datacenter', 'longName')])
    table.add_row(['Managment Ip', lb.get('managementIpAddress')])
    table.add_row(['Root Password', utils.lookup(lb, 'password', 'password')])
    table.add_row(['Primary Ip', lb.get('primaryIpAddress')])
    table.add_row(['License Expiration', utils.clean_time(lb.get('licenseExpirationDate'))])
    subnet_table = formatting.Table(['Id', 'Subnet', 'Type', 'Space'])
    for subnet in lb.get('subnets', []):
        subnet_table.add_row([
            subnet.get('id'),
            "{}/{}".format(subnet.get('networkIdentifier'), subnet.get('cidr')),
            subnet.get('subnetType'),
            subnet.get('addressSpace')
        ])
    table.add_row(['Subnets', subnet_table])

    vlan_table = formatting.Table(['Id', 'Number'])
    for vlan in lb.get('networkVlans', []):
        vlan_table.add_row([vlan.get('id'), vlan.get('vlanNumber')])
    table.add_row(['Vlans', vlan_table])

    return table
