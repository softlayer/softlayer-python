"""List hardware servers."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import formatting
from softlayer.cli import helpers
from softlayer import utils


import click


@click.command()
@click.option('--sortby',
              help='Column to sort by',
              type=click.Choice(['guid',
                                 'hostname',
                                 'primary_ip',
                                 'backend_ip',
                                 'datacenter']))
@click.option('--cpu', '-c', help='Filter by number of CPU cores')
@click.option('--domain', '-D', help='Filter by domain')
@click.option('--datacenter', '-d', help='Filter by datacenter')
@click.option('--hostname', '-H', help='Filter by hostname')
@click.option('--memory', '-m', help='Filter by memory in gigabytes')
@click.option('--network', '-n', help='Filter by network port speed in Mbps')
@helpers.multi_option('--tag', help='Filter by tags')
@environment.pass_env
def cli(env, sortby, cpu, domain, datacenter, hostname, memory, network, tag):
    """List hardware servers."""

    manager = softlayer.HardwareManager(env.client)

    servers = manager.list_hardware(hostname=hostname,
                                    domain=domain,
                                    cpus=cpu,
                                    memory=memory,
                                    datacenter=datacenter,
                                    nic_speed=network,
                                    tags=tag)

    table = formatting.Table([
        'guid',
        'hostname',
        'primary_ip',
        'backend_ip',
        'datacenter',
        'action',
    ])
    table.sortby = sortby or 'hostname'

    for server in servers:
        server = utils.NestedDict(server)
        # NOTE(kmcdonald): There are cases where a server might not have a
        #                  globalIdentifier.
        table.add_row([
            server['globalIdentifier'] or server['id'],
            server['hostname'],
            server['primaryIpAddress'] or formatting.blank(),
            server['primaryBackendIpAddress'] or formatting.blank(),
            server['datacenter']['name'] or formatting.blank(),
            formatting.active_txn(server),
        ])

    return table
