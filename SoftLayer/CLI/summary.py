"""Account summary."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


COLUMNS = ['datacenter',
           'hardware',
           'virtual_servers',
           'vlans',
           'subnets',
           'public_ips']


@click.command()
@click.option('--sortby',
              help='Column to sort by',
              default='datacenter',
              type=click.Choice(COLUMNS))
@environment.pass_env
def cli(env, sortby):
    """Account summary."""

    mgr = SoftLayer.NetworkManager(env.client)
    datacenters = mgr.summary_by_datacenter()

    table = formatting.Table(COLUMNS)
    table.sortby = sortby

    for name, datacenter in datacenters.items():
        table.add_row([
            name,
            datacenter['hardware_count'],
            datacenter['virtual_guest_count'],
            datacenter['vlan_count'],
            datacenter['subnet_count'],
            datacenter['public_ip_count'],
        ])

    env.fout(table)
