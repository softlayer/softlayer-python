"""List hardware servers."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils

import click


@click.command()
@click.option('--sortby',
              help='Column to sort by',
              type=click.Choice(['id',
                                 'datacenter',
                                 'host',
                                 'cores',
                                 'memory',
                                 'primary_ip',
                                 'backend_ip']))
@click.option('--cpu', '-c', help='Filter by number of CPU cores')
@click.option('--domain', '-D', help='Filter by domain')
@click.option('--datacenter', '-d', help='Filter by datacenter')
@click.option('--hostname', '-H', help='Filter by hostname')
@click.option('--memory', '-m', help='Filter by memory in gigabytes')
@click.option('--network', '-n', help='Filter by network port speed in Mbps')
@click.option('--tag', multiple=True, help='Filter by tags')
@environment.pass_env
def cli(env, sortby, cpu, domain, datacenter, hostname, memory, network, tag):
    """List hardware servers."""

    manager = SoftLayer.HardwareManager(env.client)

    servers = manager.list_hardware(
        hostname=hostname,
        domain=domain,
        cpus=cpu,
        memory=memory,
        datacenter=datacenter,
        nic_speed=network,
        tags=tag)

    table = formatting.Table([
        'id',
        'datacenter',
        'host',
        'cores',
        'memory',
        'primary_ip',
        'backend_ip',
        'active_transaction',
        'owner'
    ])
    table.sortby = sortby

    for server in servers:
        server = utils.NestedDict(server)

        table.add_row([
            server['id'],
            server['datacenter']['name'] or formatting.blank(),
            server['fullyQualifiedDomainName'],
            server['processorPhysicalCoreAmount'],
            formatting.gb(server['memoryCapacity'] or 0),
            server['primaryIpAddress'] or formatting.blank(),
            server['primaryBackendIpAddress'] or formatting.blank(),
            formatting.active_txn(server),
            utils.lookup(
                server, 'billingItem', 'orderItem', 'order', 'userRecord',
                'username') or formatting.blank(),
        ])

    return table
