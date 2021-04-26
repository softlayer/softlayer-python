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
            name or formatting.blank(),
            datacenter.get('hardware_count', formatting.blank()),
            datacenter.get('virtual_guest_count', formatting.blank()),
            datacenter.get('vlan_count', formatting.blank()),
            datacenter.get('subnet_count', formatting.blank()),
            datacenter.get('public_ip_count', formatting.blank()),
        ])

    env.fout(table)
