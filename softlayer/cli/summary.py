"""Account summary."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import formatting

import click


@click.command()
@click.option('--sortby',
              help='Column to sort by',
              default='datacenter',
              type=click.Choice(['datacenter',
                                 'vlans',
                                 'subnets',
                                 'ips',
                                 'networking',
                                 'hardware',
                                 'vs']))
@environment.pass_env
def cli(env, sortby):
    """Account summary."""

    mgr = softlayer.NetworkManager(env.client)
    datacenters = mgr.summary_by_datacenter()

    table = formatting.Table([
        'datacenter', 'vlans', 'subnets', 'ips', 'networking', 'hardware', 'vs'
    ])
    table.sortby = sortby

    for name, datacenter in datacenters.items():
        table.add_row([
            name,
            datacenter['vlanCount'],
            datacenter['subnetCount'],
            datacenter['primaryIpCount'],
            datacenter['networkingCount'],
            datacenter['hardwareCount'],
            datacenter['virtualGuestCount'],
        ])

    return table
